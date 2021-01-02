import setuptools

with open('README.md', 'r', encoding='utf-8') as doc:
    long_description = doc.read()

setuptools.setup(
    name='naive_ftp',
    version='0.1.1',
    author='Hakula Chen',
    author_email='i@hakula.xyz',
    description='A simple FTP server and client.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/hakula139/Naive-FTP',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Flask',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
