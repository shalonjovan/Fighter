@echo off
cls

if exist andy.re goto note
if exist dalsim.re goto note
if exist title.229 goto note

:check2
if not exist hypvega.re goto not210
if not exist bal-2.voc goto not210
if not exist hyptl.229 goto miss
if not exist hypryu.seq goto miss
if not exist hypken.seq goto miss
if not exist hypbal.re goto miss
if not exist hypvega.re goto miss
if not exist a40.voc goto configure
if not exist d7.voc goto configure
goto starthyp

rem ******************
rem * Configure game *
rem ******************

:configure
cls
echo                   THANKS FOR TRYING SFLIU V2.10!
echo.
echo Here are some tips on how to configure the game, since SF2CFG will be run
echo immediately after this message.
echo.
echo 1.  For 286 users, consider an upgrade. :) And for 386 users, you can play
echo     around with the speed setting to get the feel you want. As for 486 users
echo     you might have to crank the speed number all the way to 3700 if you have
echo     a local bus system.  It all varies, so type SF2CFG anytime to tune it.
echo.
echo Hit any key for the next page.

pause > nul
cls

echo 2.  Use the default key configuration for the least key conflicts,
echo     which is:
echo.
echo                Left Player        Right Player
echo.
echo Jump            T                  Up Arrow
echo Left            F                  Left Arrow
echo Right           H                  Right Arrow
echo Down            G                  Down Arrow
echo Jab             TAB                INS
echo Strong          Q                  HOME
echo Fierce          W                  PGUP
echo Short           CAPS LOCK          DEL
echo Forward         A                  END
echo Roundhouse      S                  PGDN
echo.
echo.
echo Hit Enter to start.  To view this message again, read SFLIU210.TXT because
echo this message will not appear the next time you run SF2.
echo.
echo Remember, use the Right Player action keys to select items from the main menu.
echo ENTER and the space bar have no effect.  For more info, refer to SFLIU210.TXT.

pause > nul

rem ****************
rem * Run SF2SETUP *
rem ****************

sf2cfg
cls

rem *******************
rem * Duplicate VOC's *
rem *******************

echo The first time SFLIU is played, it will duplicate necessary VOC files.
echo Hit a key to continue.

pause > nul

echo Now duplicating necessary files ...
echo.
echo ±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±±
copy a11.voc a14.voc > nul
blip /u
copy a11.voc a17.voc > nul
blip
copy a11.voc a20.voc > nul
blip
copy a11.voc a23.voc > nul
blip
copy a11.voc a26.voc > nul
blip
copy a11.voc a29.voc > nul
blip
copy a11.voc a32.voc > nul
blip
copy a11.voc a35.voc > nul
blip
copy a11.voc a38.voc > nul
blip
copy a12.voc a15.voc > nul
blip
copy a12.voc a18.voc > nul
blip
copy a12.voc a21.voc > nul
blip
copy a12.voc a24.voc > nul
blip
copy a12.voc a27.voc > nul
blip
copy a12.voc a30.voc > nul
blip
copy a12.voc a33.voc > nul
blip
copy a12.voc a36.voc > nul
blip
copy a12.voc a39.voc > nul
blip
copy a13.voc a16.voc > nul
blip
copy a13.voc a19.voc > nul
blip
copy a13.voc a22.voc > nul
blip
copy a13.voc a25.voc > nul
blip
copy a13.voc a28.voc > nul
blip
copy a13.voc a31.voc > nul
blip
copy a13.voc a34.voc > nul
blip
copy a13.voc a37.voc > nul
blip
copy a13.voc a40.voc > nul
blip
copy 0l.voc 1l.voc > nul
blip
copy 0l.voc 2l.voc > nul
blip
copy 0l.voc 3l.voc > nul
blip
copy 0l.voc 4l.voc > nul
blip
copy 0l.voc 5l.voc > nul
blip
copy 0l.voc 6l.voc > nul
blip
copy 0l.voc 8l.voc > nul
blip
copy 0l.voc 9l.voc > nul
blip
copy 0l.voc al.voc > nul
blip
copy 0l.voc bl.voc > nul
blip
copy 0l.voc cl.voc > nul
blip
copy c1.voc c2.voc > nul
blip
copy c4.voc c5.voc > nul
blip
copy c4.voc c7.voc > nul
blip
copy cb.voc cc.voc > nul
blip
copy d2.voc d3.voc > nul
blip
copy d2.voc d4.voc > nul
blip
copy d2.voc d5.voc > nul
blip
copy d2.voc d6.voc > nul
blip
copy d2.voc d7.voc > nul
blip
echo.
echo.
echo Done!  Hit a key to start SFLIU V2.10!

pause > nul
goto starthyp

rem *****************
rem * Missing files *
rem *****************

:miss
echo One or more of the important files needed to run this game is missing!
echo Please extract all 3 archives of the SFLIU V2.10 patch into a new
echo directory and try again.
goto end

rem ********
rem * Note *
rem ********

:note
echo SFLIU V2.10 is an independant game.  It does not need any pre-existing
echo SF2 game.  Unzip the archive to a new, empty directory to save yourself
echo disk space!
echo.
echo Hit a key to continue.
pause > nul
echo.
goto check2

rem ************
rem * Not 2.10 *
rem ************

:not210
echo Note:  You *MUST* have SFLIU V2.10 in order for V2.20 to work!
echo Install SFLIU V2.10 into a new directory, then try installing V2.20 again.
echo.
goto end

rem **************
rem * Start game *
rem **************

:starthyp
cls

echo SFLIU V2.20 Menu program
echo ------------------------
echo.
echo 1 - Run SFLIU V2.20, SSF2 mode
echo 2 - Run SFLIU V2.20, HF mode
echo 3 - Run SF2CFG.EXE
echo 4 - Read SFLIU220.TXT
echo 5 - Read SFLIU210.TXT
echo 6 - Read SFLIUFAQ.TXT
echo 7 - Read SF2MOVES.TXT
echo 8 - Read WHATSNEW.TXT
echo ESC/Q - Exit to DOS
echo.
echo Once at the main menu:
echo.
echo To move the cursor:  Right player direction keys
echo                      (default:  left/right arrows)
echo.
echo To select:           Right player attack keys
echo                      (default:  INS/HOME/PGUP/DEL/END/PGDN)
echo.
echo [Please select: (ENTER/SPACE runs #1)]

ask.exe

if errorlevel 8 goto 8
if errorlevel 7 goto 7
if errorlevel 6 goto 6
if errorlevel 5 goto 5
if errorlevel 4 goto 4
if errorlevel 3 goto 3
if errorlevel 2 goto 2
if errorlevel 1 goto 1
if errorlevel 0 goto end

:8
cls
type whatsnew.txt | more
pause
goto starthyp

:7
cls
type sf2moves.txt | more
pause
goto starthyp

:6
cls
type sfliufaq.txt | more
pause
goto starthyp

:5
cls
type sfliu210.txt | more
pause
goto starthyp

:4
cls
type sfliu220.txt | more
pause
goto starthyp

:3
cls
sf2cfg.exe
goto starthyp

:2
cls
hypsf196 hypfile.cfg
goto credits

:1
cls
supsf196 super.cfg
goto credits

:credits

rem Delete the following line if you don't want NumLock on upon exiting:
hyp-#set.com

echo Author Derek Liu - deliu@unixg.ubc.ca
echo Co-author Brian Chan - chanav@sfu.ca
echo Comments and suggestions welcomed!

:end
echo.
