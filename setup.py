import setuptools
import os
import glob


setuptools.setup(
    name='PyDomainExtractor',
    version='0.9.3',
    author='Gal Ben David',
    author_email='gal@intsights.com',
    url='https://github.com/Intsights/PyDomainExtractor',
    project_urls={
        'Source': 'https://github.com/Intsights/PyDomainExtractor',
    },
    license='MIT',
    description='Highly optimized Domain Name Extraction library written in C++',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='domain extraction tld suffix psl c++',
    python_requires='>=3.7',
    zip_safe=False,
    install_requires=[],
    package_data={},
    include_package_data=True,
    packages=setuptools.find_packages(),
    ext_package='pydomainextractor',
    ext_modules=[
        setuptools.Extension(
            name='extractor',
            sources=glob.glob(
                pathname=os.path.join(
                    'src',
                    'extractor.cpp',
                ),
            ),
            language='c++',
            extra_compile_args=[
                '-std=c++17',
            ],
            extra_link_args=[
                '-lidn2',
                '-Wl,--strip-all',
            ],
            include_dirs=[
                'src',
            ]
        ),
    ],
)
