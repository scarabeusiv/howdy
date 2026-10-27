# Installing Howdy on openSUSE

Deployment guide for the Howdy package for openSUSE, built in the OBS project
home:scarabeus_iv:howdy
(https://build.opensuse.org/package/show/home:scarabeus_iv:howdy).

Note: face authentication is skipped over SSH by default.

## 1. Install the package

    sudo zypper install howdy

Optional graphical configuration tool:

    sudo zypper install howdy-gtk

Add each user who will enrol a face to the `howdy` group, then have
that user log in again:

    sudo usermod -aG howdy <user>

## 2. Select the IR camera

List the video devices:

    v4l2-ctl --list-devices

Face recognition uses the infrared camera. On a Logitech BRIO the IR
node is /dev/video2 (greyscale, 340x340); /dev/video0 is the colour
camera, and /dev/video1 and /dev/video3 are metadata nodes. Find the
equivalent node on your hardware.

Set it in /etc/howdy/config.ini, in the [video] section:

    device_path = /dev/video2

Check the feed (the IR picture is greyscale):

    sudo howdy test

## 3. Enrol a face

Run through sudo, this enrols the invoking user:

    sudo howdy add

For another account:

    sudo howdy -U <user> add

List and remove models:

    sudo howdy list
    sudo howdy remove <id>

## 4. Activate in PAM

    sudo pam-config --add --howdy

## 5. Test, in this order

1. sudo, in a terminal:

       sudo -k whoami

   If sudo does not prompt at all, the account has a NOPASSWD rule
   and the test says nothing about Howdy.

2. KDE lock screen: lock the session and unlock it with your face.

3. Display-manager greeter: log out and log in with your face.
   This path is not yet verified end to end; its cold-boot check is
   scheduled for 2026-10-28. The sudo and lock screen tests above
   are verified.

## 6. Optional: no face login on virtual consoles

1. `cp /usr/lib/pam.d/login /etc/pam.d/login`
2. In /etc/pam.d/login, replace the `auth substack common-auth`
   line with the auth lines from /etc/pam.d/common-auth, minus the
   `pam_howdy.so` line.
3. Revert with: `sudo rm /etc/pam.d/login`

pam-config manages the common stack only; re-sync this override by
hand when the common stack changes.

## 7. Troubleshooting

- No face found, or the test feed is in colour: device_path points
  at the colour camera or a metadata node. Redo step 2.
- Every frame black: the IR emitter is covered, or you are out of
  range. Unlit frames between emitter flashes are normal and are
  skipped automatically.

Disable face authentication again:

    sudo pam-config --delete --howdy
