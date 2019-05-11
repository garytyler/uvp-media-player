from setuptools import setup

setup(
    name="eventvr-player",
    version="0.1",
    module=["eventvr_player"],
    include_package_data=True,
    install_requires=["click", "PyQt5", "python-vlc"],
)
