use ahash::{AHashMap, AHashSet};
use pyo3::exceptions::PyValueError;
use pyo3::intern;
use pyo3::prelude::*;
use pyo3::types::PyString;

type DomainString = arraystring::ArrayString<typenum::U255>;

#[derive(Default)]
struct Suffix {
    sub_suffixes: AHashMap<String, Suffix>,
    is_wildcard: bool,
    sub_blacklist: AHashSet<String>,
}

static PUBLIC_SUFFIX_LIST_DATA: &str = include_str!("public_suffix_list.dat");

#[pyclass]
struct DomainExtractor {
    suffixes: AHashMap<String, Suffix>,
    tld_list: Vec<String>,
}

#[pymethods]
impl DomainExtractor {
    #[new]
    fn new(
        suffix_list: Option<&str>,
    ) -> Self {
        let (suffixes, tld_list) = if let Some(suffix_list) = suffix_list {
            parse_suffix_list(suffix_list)
        } else {
            parse_suffix_list(PUBLIC_SUFFIX_LIST_DATA)
        };

        DomainExtractor { suffixes, tld_list }
    }

    fn parse_domain_parts<'a>(
        &self,
        domain: &'a str,
    ) -> PyResult<(&'a str, &'a str, &'a str)> {
        let mut suffix_part = "";
        let mut current_suffixes = &self.suffixes;
        let mut last_dot_index = domain.len();
        let mut in_wildcard_tld = false;
        let mut last_suffix: Option<&Suffix> = None;

        while let Some(dot_index) = memchr::memrchr(b'.', &domain.as_bytes()[..last_dot_index]) {
            let current_fraction = &domain[dot_index + 1..last_dot_index];
            if current_fraction.is_empty() || dot_index == 0 {
                return Err(PyValueError::new_err("Invalid domain detected"));
            }

            if in_wildcard_tld {
                if last_suffix.unwrap().sub_blacklist.contains(current_fraction) {
                    let leftover_part = &domain[0..dot_index];

                    return Ok((suffix_part, current_fraction, leftover_part));
                }

                if let Some(current_suffix) = current_suffixes.get(current_fraction) {
                    if !current_suffix.is_wildcard {
                        current_suffixes = &current_suffix.sub_suffixes;
                    }
                    last_suffix.replace(current_suffix);
                    suffix_part = &domain[dot_index + 1..];
                    last_dot_index = dot_index;
                } else {
                    suffix_part = &domain[dot_index + 1..];
                    let leftover_part = &domain[0..dot_index];
                    match leftover_part.rsplit_once('.') {
                        Some((subdomain_part, domain_part)) => {
                            if subdomain_part.ends_with('.') {
                                return Err(PyValueError::new_err("Invalid domain detected"));
                            }
                            return Ok((suffix_part, domain_part, subdomain_part));
                        }
                        None => {
                            return Ok((suffix_part, leftover_part, ""));
                        }
                    }
                }
            }
            if let Some(current_suffix) = current_suffixes.get(current_fraction) {
                in_wildcard_tld = current_suffix.is_wildcard;

                current_suffixes = &current_suffix.sub_suffixes;
                last_suffix.replace(current_suffix);
                suffix_part = &domain[dot_index + 1..];
                last_dot_index = dot_index;
            } else {
                let leftover_part = &domain[0..last_dot_index];
                match leftover_part.rsplit_once('.') {
                    Some((subdomain_part, domain_part)) => {
                        if subdomain_part.ends_with('.') {
                            return Err(PyValueError::new_err("Invalid domain detected"));
                        }
                        return Ok((suffix_part, domain_part, subdomain_part));
                    }
                    None => {
                        return Ok((suffix_part, leftover_part, ""));
                    }
                };
            }
        }

        let current_fraction = &domain[0..last_dot_index];
        if in_wildcard_tld {
            if last_suffix.unwrap().sub_blacklist.contains(current_fraction) {
                Ok((suffix_part, current_fraction, ""))
            } else {
                Ok((domain, "", ""))
            }
        } else if current_suffixes.len() > 0 && current_suffixes.contains_key(current_fraction) {
            Ok((domain, "", ""))
        } else {
            Ok((suffix_part, current_fraction, ""))
        }
    }

    fn extract(
        &self,
        py: Python,
        domain: &PyString,
    ) -> PyResult<PyObject> {
        if domain.len().unwrap() > 255 {
            return Err(PyValueError::new_err("Invalid domain detected"));
        }

        let mut domain_string = unsafe {
            DomainString::from_str_unchecked(domain.to_string_lossy().as_ref())
        };
        domain_string.make_ascii_lowercase();

        let (suffix_part, domain_part, subdomain_part) = self.parse_domain_parts(domain_string.as_str())?;

        unsafe {
            let dict = pyo3::ffi::PyDict_New();
            for (fraction_key, fraction) in [
                (intern!(py, "suffix").into_ptr(), suffix_part),
                (intern!(py, "domain").into_ptr(), domain_part),
                (intern!(py, "subdomain").into_ptr(), subdomain_part),
            ] {
                if !fraction.is_empty() {
                    let substr = pyo3::ffi::PyUnicode_FromStringAndSize(
                        fraction.as_ptr() as *const i8,
                        fraction.len() as isize,
                    );

                    pyo3::ffi::PyDict_SetItem(
                        dict,
                        fraction_key,
                        substr,
                    );
                    pyo3::ffi::Py_DECREF(substr);
                } else {
                    pyo3::ffi::PyDict_SetItem(
                        dict,
                        fraction_key,
                        intern!(py, "").into_ptr(),
                    );
                }
            }

            Ok(pyo3::PyObject::from_owned_ptr(py, dict))
        }
    }

    fn is_valid_domain(
        &self,
        domain: &PyString,
    ) -> bool {
        let domain_len = domain.len().unwrap();
        if domain_len == 0 || domain_len > 255 {
            return false;
        }

        let mut domain_string = unsafe {
            DomainString::from_str_unchecked(domain.to_string_lossy().as_ref())
        };

        for fraction in domain_string.split('.') {
            if fraction.len() > 63 || fraction.is_empty() {
                return false;
            }
            if fraction.starts_with('-') || fraction.ends_with('-') {
                return false;
            }

            for ch in fraction.chars() {
                if !ch.is_alphanumeric() && ch != '-' {
                    return false;
                }
            }
        }

        domain_string.make_ascii_lowercase();
        if let Ok((suffix_part, domain_part, _subdomain_part)) = self.parse_domain_parts(domain_string.as_str()) {
            if suffix_part.is_empty() || domain_part.is_empty() {
                return false;
            }

            if idna::domain_to_ascii(domain_string.as_str()).is_err() {
                return false;
            }
            if idna::domain_to_unicode(domain_string.as_str()).1.is_err() {
                return false;
            }

            true
        } else {
            false
        }
    }

    fn get_tld_list(
        &self,
    ) -> Vec<String> {
        self.tld_list.clone()
    }

    fn extract_from_url(
        &self,
        py: Python,
        url: &PyString,
    ) -> PyResult<PyObject> {
        let mut url_str = url.to_str().unwrap();

        match memchr::memmem::find(url_str.as_bytes(), b"//") {
            Some(scheme_separator_position) => {
                url_str = &url_str[scheme_separator_position + 2..];
            },
            None => return Err(
                PyValueError::new_err("url is invalid: no scheme")
            ),
        };

        if let Some(path_separator) = memchr::memchr(b'/', url_str.as_bytes()) {
            url_str = &url_str[..path_separator];
        };

        if let Some(authentication_separator) = memchr::memchr(b'@', url_str.as_bytes()) {
            url_str = &url_str[authentication_separator + 1..];
        };

        if let Some(port_separator) = memchr::memchr(b':', url_str.as_bytes()) {
            url_str = &url_str[..port_separator];
        };

        if url_str.is_empty() {
            return Err(
                PyValueError::new_err("url does not contain a domain")
            );
        }

        let mut domain_string = unsafe {
            DomainString::from_str_unchecked(url_str)
        };
        domain_string.make_ascii_lowercase();

        let (suffix_part, domain_part, subdomain_part) = self.parse_domain_parts(domain_string.as_str())?;

        unsafe {
            let dict = pyo3::ffi::PyDict_New();
            for (fraction_key, fraction) in [
                (intern!(py, "suffix").into_ptr(), suffix_part),
                (intern!(py, "domain").into_ptr(), domain_part),
                (intern!(py, "subdomain").into_ptr(), subdomain_part),
            ] {
                if !fraction.is_empty() {
                    let substr = pyo3::ffi::PyUnicode_FromStringAndSize(
                        fraction.as_ptr() as *const i8,
                        fraction.len() as isize,
                    );

                    pyo3::ffi::PyDict_SetItem(
                        dict,
                        fraction_key,
                        substr,
                    );
                    pyo3::ffi::Py_DECREF(substr);
                } else {
                    pyo3::ffi::PyDict_SetItem(
                        dict,
                        fraction_key,
                        intern!(py, "").into_ptr(),
                    );
                }
            }

            Ok(pyo3::PyObject::from_owned_ptr(py, dict))
        }
    }
}

fn parse_suffix_list(
    suffixes_list: &str,
) -> (AHashMap<String, Suffix>, Vec<String>) {
    let mut suffixes = AHashMap::new();
    let mut tld_list = Vec::new();

    for line in suffixes_list.lines().map(
        |line| line.to_ascii_lowercase()
    ) {
        if line.starts_with("//") || line.is_empty() {
            continue;
        }

        let mut tlds = vec![line.clone()];
        if !line.is_ascii() {
            tlds.push(idna::domain_to_ascii(&line).unwrap());
        }
        for tld in tlds {
            tld_list.push(tld.clone());

            let fractions: Vec<String> = tld.rsplit('.').map(
                |s| s.to_string()
            ).collect();
            let mut current_suffix = suffixes.entry(fractions.first().unwrap().to_owned()).or_insert(
                Suffix {
                    sub_suffixes: AHashMap::new(),
                    is_wildcard: false,
                    sub_blacklist: AHashSet::new(),
                }
            );

            for fraction in fractions[1..].iter() {
                if fraction.starts_with('!') {
                    current_suffix.sub_blacklist.insert(fraction.strip_prefix('!').unwrap().to_string());
                } else if fraction == "*" {
                    current_suffix.is_wildcard = true;
                } else {
                    current_suffix = current_suffix.sub_suffixes.entry(fraction.clone()).or_insert(
                        Suffix {
                            sub_suffixes: AHashMap::new(),
                            is_wildcard: false,
                            sub_blacklist: AHashSet::new(),
                        }
                    );
                }
            }
        }
    }

    (suffixes, tld_list)
}

#[pymodule]
fn pydomainextractor(
    _py: Python,
    m: &PyModule,
) -> PyResult<()> {
    m.add_class::<DomainExtractor>()?;
    Ok(())
}
