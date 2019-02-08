from setuptools import setup


setup(
    name="vrpclient",
    version="0.1",
    packages=["vrpclient"],
    include_package_data=True,
    install_requires=["click", "python-socketio", "urllib3"],
    entry_points={"console_scripts": ["vrpclient=vrpclient.cli:cli"]},
)
