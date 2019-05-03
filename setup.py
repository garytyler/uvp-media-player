from setuptools import setup


setup(
    name="seevr-player",
    version="0.1",
<<<<<<< HEAD
<<<<<<< HEAD
    packages=["seevr_player"],
    include_package_data=True,
    install_requires=["click", "python-socketio", "urllib3", "PyQt5", "python-vlc"],
    # entry_points={"console_scripts": ["seevr_player=seevr_player:cli"]},
=======
    packages=["seevrplayer"],
    include_package_data=True,
    install_requires=["click", "python-socketio", "urllib3", "PyQt5", "python-vlc"],
    entry_points={"console_scripts": ["seevrplayer=seevrplayer:cli"]},
>>>>>>> 39d3b3b... Change name to seevr
=======
    packages=["seevrplayer"],
    include_package_data=True,
    install_requires=["click", "python-socketio", "urllib3", "PyQt5", "python-vlc"],
    entry_points={"console_scripts": ["seevrplayer=seevrplayer:cli"]},
>>>>>>> 39d3b3bea4b6b4f4768be8d3e22c7a07116c7e0e
)
