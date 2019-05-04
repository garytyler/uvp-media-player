from setuptools import setup


setup(
    name="seevr-player",
    version="0.1",
    packages=["seevr_player"],
    include_package_data=True,
    install_requires=["click", "PyQt5", "python-vlc"],
    entry_points={"console_scripts": ["seevrplayer=seevr_player:cli"]},
)
