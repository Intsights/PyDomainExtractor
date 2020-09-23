#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>
#include <unordered_set>
#include <string>
#include <string_view>
#include <cstring>
#include <sstream>
#include <locale>
#include <codecvt>
#include <memory>
#include <idn2.h>
#include <tsl/robin_set.h>

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
                } else if (line.find("!") != std::string::npos) {
                    std::string clean_tld = line.substr(1);
                    auto permutations = this->get_all_permutations(clean_tld, false);
                    for (const auto & permutation : permutations) {
                        this->blacklisted_tlds.emplace(permutation);
                    }
                } else if (line.find("*") != std::string::npos) {
                    std::string clean_tld = line.substr(2);
                    auto permutations = this->get_all_permutations(clean_tld, false);
                    for (const auto & permutation : permutations) {
                        this->wildcard_tlds.emplace(permutation);
                        this->known_tlds.emplace(permutation);
                    }
                } else {
                    auto permutations = this->get_all_permutations(line, true);
                    for (const auto & permutation : permutations) {
                        this->known_tlds.emplace(permutation);
                    }
                }
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

        std::unordered_set<std::string> get_all_permutations(
            const std::string & tld,
            bool permutate_sub_tlds
        ) {
            std::unordered_set<std::string> translations;
            std::unordered_set<std::string> permutations;
            char * conversion_buffer = NULL;

            translations.emplace(tld);

            if (IDN2_OK == idn2_to_ascii_8z(tld.c_str(), &conversion_buffer, IDN2_NONTRANSITIONAL)) {
                translations.emplace(std::string(conversion_buffer));
            }
            if (conversion_buffer != NULL) {
                idn2_free(conversion_buffer);
            }

            if (IDN2_OK == idn2_to_unicode_8z8z(tld.c_str(), &conversion_buffer, IDN2_NONTRANSITIONAL)) {
                translations.emplace(std::string(conversion_buffer));
            }
            if (conversion_buffer != NULL) {
                idn2_free(conversion_buffer);
            }

            for (const auto & translation : translations) {
                permutations.emplace(translation);

                if (permutate_sub_tlds) {
                    auto current_position = 0;
                    while (translation.find('.', current_position) != std::string::npos) {
                        std::string current_sliced_translation = translation.substr(translation.find('.', current_position) + 1);
                        permutations.emplace(current_sliced_translation);
                        current_position = translation.find('.', current_position) + 1;
                    }
                }
            }

            return permutations;
        }

        inline std::tuple<std::string_view, std::string_view, std::string_view> extract(
            std::string_view domain
        ) {
            if (
                domain.empty() ||
                domain.front() == '.' ||
                domain.back() == '.' ||
                domain.find("..") != std::string::npos
            ) {
                throw std::runtime_error("Invalid domain detected");
            }

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

        inline std::string_view extract_suffix(
            std::string_view domain
        ) noexcept {
            std::string_view extracted_suffix;
            std::size_t last_period_position = domain.find_last_of('.');
            if (last_period_position == std::string::npos) {
                if (this->known_tlds_views.contains(domain) == true) {
                    return domain;
                } else {
                    return "";
                }
            }

            while (true) {
                std::string_view current_suffix = domain.substr(last_period_position + 1);
                if (this->known_tlds_views.contains(current_suffix) == false) {
                    break;
                }
                extracted_suffix = current_suffix;
                last_period_position = domain.find_last_of('.', last_period_position - 1);
                if (last_period_position == std::string::npos) {
                    if (this->known_tlds_views.contains(domain) == true) {
                        extracted_suffix = domain;
                    }

                    break;
                }
            }

            if (this->wildcard_tlds_views.contains(extracted_suffix) == true) {
                std::size_t leftover_domain_size = domain.size() - extracted_suffix.size() - 1;
                if (leftover_domain_size > 0) {
                    std::size_t period_position = domain.find_last_of('.', leftover_domain_size - 1);
                    if (period_position == std::string::npos) {
                        if (this->blacklisted_tlds_views.contains(domain) == false) {
                            return domain;
                        } else {
                            return extracted_suffix;
                        }
                    } else {
                        if (this->blacklisted_tlds_views.contains(domain.substr(period_position + 1)) == true) {
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

        inline bool is_valid_domain(
            const std::string & domain
        ) {
            if (domain.size() > 255) {
                return false;
            }

            std::string domain_part;
            std::istringstream domain_parts_stream(domain);
            while (std::getline(domain_parts_stream, domain_part, '.')) {
                if (domain_part.size() > 63 || domain_part.empty()) {
                    return false;
                }

                if (domain_part.front() == '-' || domain_part.back() == '-') {
                    return false;
                }

                std::u16string domain_part_utf16 = std::wstring_convert<std::codecvt_utf8_utf16<char16_t>, char16_t>{}.from_bytes(domain_part.data());
                for (const auto & ch : domain_part_utf16) {
                    if (std::iswalnum(ch) == false && ch != '-') {
                        return false;
                    }
                }
            }

            try {
                const auto & [subdomain, domain_name, suffix] = this->extract(domain);
                if (suffix.empty() || domain_name.empty()) {
                    return false;
                }
            } catch (...) {
                return false;
            }

            char * conversion_buffer = NULL;
            int idn2_to_ascii_result = idn2_to_ascii_8z(
                domain.c_str(),
                &conversion_buffer,
                IDN2_NONTRANSITIONAL | IDN2_NFC_INPUT
            );
            if (conversion_buffer != NULL) {
                idn2_free(conversion_buffer);
                conversion_buffer = NULL;
            }
            if (IDN2_OK != idn2_to_ascii_result) {
                return false;
            }

            int idn2_to_unicode_result = idn2_to_unicode_8z8z(
                domain.c_str(),
                &conversion_buffer,
                IDN2_NONTRANSITIONAL | IDN2_NFC_INPUT
            );
            if (conversion_buffer != NULL) {
                idn2_free(conversion_buffer);
                conversion_buffer = NULL;
            }
            if (IDN2_OK != idn2_to_unicode_result) {
                return false;
            }

            return true;
        }

        tsl::robin_set<std::string> known_tlds;
        tsl::robin_set<std::string> blacklisted_tlds;
        tsl::robin_set<std::string> wildcard_tlds;
        tsl::robin_set<std::string_view> known_tlds_views;
        tsl::robin_set<std::string_view> blacklisted_tlds_views;
        tsl::robin_set<std::string_view> wildcard_tlds_views;
};


typedef struct {
    PyObject_HEAD
    std::unique_ptr<DomainExtractor> domain_extractor;
} DomainExtractorObject;


static void DomainExtractor_dealloc(DomainExtractorObject *self) {
    Py_TYPE(self)->tp_free((PyObject *) self);
    self->domain_extractor.reset();
}


static PyObject * DomainExtractor_new(PyTypeObject *type, PyObject *args, PyObject *kwds) {
    DomainExtractorObject *self;
    self = (DomainExtractorObject *) type->tp_alloc(type, 0);

    return (PyObject *) self;
}


static int DomainExtractor_init(DomainExtractorObject *self, PyObject *args, PyObject *kwds) {
    const char * suffix_list_data = "";

    static char * kwlist[] = {
        (char *)"suffix_list_data",
        NULL
    };

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|s", kwlist, &suffix_list_data)) {
        return -1;
    }


    if (strlen(suffix_list_data) == 0) {
        self->domain_extractor = std::make_unique<DomainExtractor>(PSL::public_suffix_list_data);
    } else {
        self->domain_extractor = std::make_unique<DomainExtractor>(suffix_list_data);
    }

    return 0;
}


static PyMemberDef DomainExtractor_members[] = {
    {NULL}
};


PyObject * subdomain_key_py = PyUnicode_FromString("subdomain");
PyObject * domain_key_py = PyUnicode_FromString("domain");
PyObject * suffix_key_py = PyUnicode_FromString("suffix");
static PyObject * DomainExtractor_extract(
    DomainExtractorObject * self,
    PyObject * arg
) {
    const char * input = PyUnicode_AsUTF8(arg);

    try {
        auto extracted_domain = self->domain_extractor->extract(input);

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
    } catch (const std::runtime_error &exception) {
        PyErr_SetString(PyExc_ValueError, exception.what());

        return NULL;
    }
}


static PyObject * DomainExtractor_extract_from_url(
    DomainExtractorObject * self,
    PyObject * arg
) {
    const char * input = PyUnicode_AsUTF8(arg);
    std::string_view url(input);

    std::size_t scheme_separator_position = url.find("//");
    if (scheme_separator_position == std::string::npos) {
        PyErr_SetString(PyExc_ValueError, "url is invalid: no scheme");

        return NULL;
    }
    url = url.substr(scheme_separator_position + 2);

    std::size_t path_separator = url.find("/");
    if (path_separator != std::string::npos) {
        url = url.substr(0, path_separator);
    }

    std::size_t authentication_separator = url.find("@");
    if (authentication_separator != std::string::npos) {
        url = url.substr(authentication_separator + 1);
    }

    std::size_t port_separator = url.find(":");
    if (port_separator != std::string::npos) {
        url = url.substr(0, port_separator);
    }

    try {
        auto extracted_domain = self->domain_extractor->extract(url);

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

    } catch (const std::runtime_error &exception) {
        PyErr_SetString(PyExc_ValueError, exception.what());

        return NULL;
    }
}


static PyObject * DomainExtractor_is_valid_domain(
    DomainExtractorObject * self,
    PyObject * arg
) {
    const char * input = PyUnicode_AsUTF8(arg);

    auto valid_domain = self->domain_extractor->is_valid_domain(std::string(input));
    if (valid_domain == true) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
}


static PyObject * DomainExtractor_get_tld_list(
    DomainExtractorObject * self,
    PyObject * const* noargs
) {
    auto tlds = PyList_New(self->domain_extractor->known_tlds.size());
    int i = 0;
    for (auto tld: self->domain_extractor->known_tlds) {
        PyList_SET_ITEM(tlds, i, PyUnicode_FromString(tld.c_str()));
        i++;
    }

    return tlds;
}


static PyMethodDef DomainExtractor_methods[] = {
    {
        "extract",
        (PyCFunction)DomainExtractor_extract,
        METH_O,
        "Extract a domain string into its parts\n\nextract(domain)\nArguments:\n\tdomain(str): the domain string to extract\nReturn:\n\tdict[str, str] -> The extracted parts as 'subdomain', 'domain', 'suffix'\n\n"
    },
    {
        "extract_from_url",
        (PyCFunction)DomainExtractor_extract_from_url,
        METH_O,
        "Extract a domain from a url into its parts\n\nextract_from_url(url)\nArguments:\n\turl(str): the url string to extract\nReturn:\n\tdict[str, str] -> The extracted parts as 'subdomain', 'domain', 'suffix'\n\n"
    },
    {
        "is_valid_domain",
        (PyCFunction)DomainExtractor_is_valid_domain,
        METH_O,
        "Checks whether a domain is a valid domain\n\nis_valid_domain(domain)\nArguments:\n\tdomain(str): the domain string to validate\nReturn:\n\tbool: True if valid or False if invalid\n\n"
    },
    {
        "get_tld_list",
        (PyCFunction)DomainExtractor_get_tld_list,
        METH_NOARGS,
        "Return a list of all the known tlds\n\nget_tld_list()\nArguments:\n\tNone\nReturn:\n\tlist[str]: list of tlds\n\n"
    },
    {NULL}  /* Sentinel */
};


static PyTypeObject DomainExtractorType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "pydomainextractor.DomainExtractor", /* tp_name */
    sizeof(DomainExtractorObject), /* tp_basicsize */
    0, /* tp_itemsize */
    (destructor)DomainExtractor_dealloc, /* tp_dealloc */
    0, /* tp_print */
    0, /* tp_getattr */
    0, /* tp_setattr */
    0, /* tp_reserved */
    0, /* tp_repr */
    0, /* tp_as_number */
    0, /* tp_as_sequence */
    0, /* tp_as_mapping */
    0, /* tp_hash */
    0, /* tp_call */
    0, /* tp_str */
    0, /* tp_getattro */
    0, /* tp_setattro */
    0, /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /* tp_flags */
    "PyDomainExtractor is a highly optimized Domain Name Extraction library written in C++ ", /* tp_doc */
    0, /* tp_traverse */
    0, /* tp_clear */
    0, /* tp_richcompare */
    0, /* tp_weaklistoffset */
    0, /* tp_iter */
    0, /* tp_iternext */
    DomainExtractor_methods, /* tp_methods */
    DomainExtractor_members, /* tp_members */
    0, /* tp_getset */
    0, /* tp_base */
    0, /* tp_dict */
    0, /* tp_descr_get */
    0, /* tp_descr_set */
    0, /* tp_dictoffset */
    (initproc)DomainExtractor_init, /* tp_init */
    0, /* tp_alloc */
    DomainExtractor_new /* tp_new */
};


static struct PyModuleDef pydomainextractor_definition = {
    PyModuleDef_HEAD_INIT,
    "pydomainextractor",
    "Extracting domain strings into their parts",
    -1,
    NULL,
};


PyMODINIT_FUNC
PyInit_pydomainextractor(void) {
    PyObject *m;
    if (PyType_Ready(&DomainExtractorType) < 0) {
        return NULL;
    }

    m = PyModule_Create(&pydomainextractor_definition);
    if (m == NULL) {
        return NULL;
    }

    Py_INCREF(&DomainExtractorType);
    if (PyModule_AddObject(m, "DomainExtractor", (PyObject *) &DomainExtractorType) < 0) {
        Py_DECREF(&DomainExtractorType);
        Py_DECREF(m);

        return NULL;
    }

    return m;
}
