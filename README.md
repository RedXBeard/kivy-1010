# kivy-1010
1010 game implemented on python kivy for desktops

## Releases
<a href="url"><img src="http://s10.postimg.org/g8rs7ptkp/Screen_Shot_2015_03_25_at_13_13_39png" align="right" height="370" width="300" ></a>

##### 1.0.0
- First release.

##### 1.1.0
- Rotation, scaling actions of shapes bug fixed.

##### 1.2.0
- Free position calculation bug fixed.
- Code cleaned.
- Performance fixes.

##### 1.3.0
- Sound effects added.
- Session saved on exit.
- Window width-height fixing disabled.
- Shapes probability of appearing calculation fixed.

##### 1.4.0
- Version control added on start popup.
- Session saved on exit extended.
- On window resizing, board and shapes take effect.
- Optimum window size considered.
- Shapes colours are unique on each session.

##### 1.5.0
- Theme changed.
- Android / IOS style served.
- Calculation process extended of sizes and positions.
- Package size eliminated.
- Original game shapes applied. 

## Installation

#### For MacOS
Download and install <code>.dmg</code> file from [MacOSX file](https://app.box.com/s/k62rafyc2a0e80h88crn9km274123eqi)

#### For Linux
Run the following commands;
```
sudo add-apt-repository ppa:kivy-team/kivy-daily
sudo apt-get update
sudo apt-get install python-kivy
git clone https://github.com/RedXBeard/kivy-1010.git
```
To create a launcher just type the following;
```
gnome-desktop-item-edit --create-new ~/.local/share/applications/.
```
On launcher window type;

<code>Kivy1010</code> in name box, 

<code>python /repository/path/main.py</code> in command box, 

application icon path is <code>/repository/path/assets/images/cubepng</code> then 

click <code>ok</code>. 

Application is now reachable from the menu.


#### For Windows
Download and <code>.zip</code> file from [windows file](https://app.box.com/s/2zf82w8gxv1w31m4vsi6xkz4eceaqdae) then unzip file to program files folder create shortcut of <code>.exe</code> in unzipped folder to the desktop then it is ready to run
