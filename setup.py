from setuptools import setup


setup(
    name="seevr-player",
    version="0.1",
    packages=["seevrplayer"],
    include_package_data=True,
    install_requires=["click", "python-socketio", "urllib3", "PyQt5", "python-vlc"],
    entry_points={"console_scripts": ["seevrplayer=seevrplayer:cli"]},
)
