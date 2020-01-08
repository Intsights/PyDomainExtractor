#include <Python.h>
#include <unordered_set>
#include <string>
#include <cstring>
#include <sstream>
#include <memory>
#include <idn2.h>

#include "public_suffix_list.h"


class DomainExtractor {
    public:
        DomainExtractor(
            std::string suffix_list_data
        ) {
            std::istringstream suffix_list_data_stream(suffix_list_data);
            std::string line;

            while (std::getline(suffix_list_data_stream, line)) {
                if (line.find("//") != std::string::npos || line.empty()) {
                    continue;
                }

                if (line.find("!") != std::string::npos) {
                    this->blacklisted_tlds.emplace(std::string(line.substr(1)));

                    continue;
                }

                if (line.find("*") != std::string::npos) {
                    this->wildcard_tlds.emplace(std::string(line.substr(2)));
                    line = line.substr(2);
                }

                char *conversion_buffer;
                if (IDNA_SUCCESS == idn2_to_ascii_8z(line.c_str(), &conversion_buffer, IDN2_NONTRANSITIONAL)) {
                    this->known_tlds.emplace(std::string(conversion_buffer));
                }
                free(conversion_buffer);

                this->known_tlds.emplace(line);
            }

            for (auto const & known_tld : this->known_tlds) {
                this->known_tlds_views.emplace(std::string_view(known_tld));
            }
            for (auto const & blacklisted_tld : this->blacklisted_tlds) {
                this->blacklisted_tlds_views.emplace(std::string_view(blacklisted_tld));
            }
            for (auto const & wildcard_tld : this->wildcard_tlds) {
                this->wildcard_tlds_views.emplace(std::string_view(wildcard_tld));
            }
        }
        ~DomainExtractor() {}

        const inline std::tuple<std::string_view, std::string_view, std::string_view> extract(
            std::string_view domain
        ) noexcept {
            for (auto & domain_char : domain) {
                if (domain_char >= 'A' && domain_char <= 'Z') {
                    const_cast<char&>(domain_char) = domain_char + 32;
                }
            }
            std::string_view extracted_suffix = this->extract_suffix(domain);

            std::string_view domain_part;
            if (extracted_suffix.empty()) {
                domain_part = domain;
            } else if (extracted_suffix.size() == domain.size()) {
                domain_part = "";
            } else {
                domain_part = domain.substr(0, domain.size() - extracted_suffix.size() - 1);
            }
            std::size_t last_domain_period_position = domain_part.find_last_of('.');

            if (last_domain_period_position == std::string::npos) {
                return std::make_tuple(
                    "",
                    domain_part.substr(0, last_domain_period_position),
                    extracted_suffix
                );
            } else {
                return std::make_tuple(
                    domain_part.substr(0, last_domain_period_position),
                    domain_part.substr(last_domain_period_position + 1),
                    extracted_suffix
                );
            }
        }

        const inline std::string_view extract_suffix(
            std::string_view domain
        ) noexcept {
            std::string_view extracted_suffix;
            std::size_t last_period_position = domain.find_last_of('.');
            if (last_period_position == std::string::npos) {
                if (this->known_tlds_views.count(domain) == 1) {
                    return domain;
                } else {
                    return "";
                }
            }

            while (true) {
                std::string_view current_suffix = domain.substr(last_period_position + 1);
                if (this->known_tlds_views.count(current_suffix) == 0) {
                    break;
                }
                extracted_suffix = current_suffix;
                last_period_position = domain.find_last_of('.', last_period_position - 1);
                if (last_period_position == std::string::npos) {
                    if (this->known_tlds_views.count(domain) == 1) {
                        extracted_suffix = domain;
                    }

                    break;
                }
            }

            if (this->wildcard_tlds_views.count(extracted_suffix) == 1) {
                std::size_t leftover_domain_size = domain.size() - extracted_suffix.size() - 1;
                if (leftover_domain_size > 0) {
                    std::size_t period_position = domain.find_last_of('.', leftover_domain_size - 1);
                    if (period_position == std::string::npos) {
                        if (this->blacklisted_tlds_views.count(domain) == 0) {
                            return domain;
                        } else {
                            return extracted_suffix;
                        }
                    } else {
                        if (this->blacklisted_tlds_views.count(domain.substr(period_position + 1)) == 1) {
                            return extracted_suffix;
                        } else {
                            return domain.substr(period_position + 1);
                        }
                    }
                } else {
                    return extracted_suffix;
                }
            } else {
                return extracted_suffix;
            }
        }

        std::unordered_set<std::string> known_tlds;
        std::unordered_set<std::string> blacklisted_tlds;
        std::unordered_set<std::string> wildcard_tlds;
        std::unordered_set<std::string_view> known_tlds_views;
        std::unordered_set<std::string_view> blacklisted_tlds_views;
        std::unordered_set<std::string_view> wildcard_tlds_views;
};


std::unique_ptr<DomainExtractor> domain_extractor = nullptr;
static PyObject * load(
    PyObject * self,
    PyObject * args,
    PyObject * kwds
) {
    const char * suffix_list_data = "";

    static char * kwlist[] = {
        (char *)"suffix_list_data",
        NULL
    };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|s", kwlist, &suffix_list_data)) {
        return NULL;
    } else {
        if (strlen(suffix_list_data) == 0) {
            domain_extractor = std::make_unique<DomainExtractor>(PSL::public_suffix_list_data);
        } else {
            domain_extractor = std::make_unique<DomainExtractor>(suffix_list_data);
        }

        Py_RETURN_NONE;
    }
}


static PyObject * unload(
    PyObject * self
) {
    if (domain_extractor != nullptr) {
        domain_extractor.release();
        domain_extractor = nullptr;
    }

    Py_RETURN_NONE;
}


PyObject * subdomain_key_py = PyUnicode_FromString("subdomain");
PyObject * domain_key_py = PyUnicode_FromString("domain");
PyObject * suffix_key_py = PyUnicode_FromString("suffix");
static PyObject * extract(
    PyObject * self,
    PyObject * const* args,
    Py_ssize_t nargs
) {
    if (domain_extractor == nullptr) {
        PyErr_SetString(PyExc_ValueError, "Suffix list was not loaded. Call for load() first");

        return NULL;
    }

    if (nargs != 1) {
        PyErr_SetString(PyExc_ValueError, "wrong number of arguments");

        return NULL;
    }

    const char * input = PyUnicode_AsUTF8(args[0]);

    auto extracted_domain = domain_extractor->extract(input);

    PyObject * dict = PyDict_New();

    PyObject * subdomain_py = PyUnicode_DecodeUTF8(
        std::get<0>(extracted_domain).data(),
        std::get<0>(extracted_domain).size(),
        NULL
    );
    PyObject * domain_py = PyUnicode_DecodeUTF8(
        std::get<1>(extracted_domain).data(),
        std::get<1>(extracted_domain).size(),
        NULL
    );
    PyObject * suffix_py = PyUnicode_DecodeUTF8(
        std::get<2>(extracted_domain).data(),
        std::get<2>(extracted_domain).size(),
        NULL
    );

    PyDict_SetItem(
        dict,
        PyUnicode_FromObject(subdomain_key_py),
        subdomain_py
    );
    PyDict_SetItem(
        dict,
        PyUnicode_FromObject(domain_key_py),
        domain_py
    );
    PyDict_SetItem(
        dict,
        PyUnicode_FromObject(suffix_key_py),
        suffix_py
    );

    Py_DECREF(subdomain_py);
    Py_DECREF(domain_py);
    Py_DECREF(suffix_py);

    return dict;
}


static PyMethodDef pydomainextractor_methods[] = {
    {
        "extract",
        (PyCFunction)extract,
        METH_FASTCALL,
        "Extract a domain string into its parts\n\nextract(domain)\nArguments:\n\tdomain(str): the domain string to extract\nReturn:\n\ttuple(str, str, str): subdomain, domain, suffix\n\n"
    },
    {
        "load",
        (PyCFunction)load,
        METH_VARARGS | METH_KEYWORDS,
        "Loads a public suffix list data"
    },
    {
        "unload",
        (PyCFunction)unload,
        METH_NOARGS,
        "Release the public suffix list object"
    },
    {
        NULL,
        NULL,
        0,
        NULL
    },
};


static struct PyModuleDef pydomainextractor_definition = {
    PyModuleDef_HEAD_INIT,
    "pydomainextractor",
    "Extracting domain strings into their parts",
    -1,
    pydomainextractor_methods,
};


PyMODINIT_FUNC PyInit_pydomainextractor(void) {
    Py_Initialize();

    PyObject * m = PyModule_Create(&pydomainextractor_definition);

    return m;
}
