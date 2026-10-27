# Deploying the openSUSE Howdy package

The changes carried by this fork (scarabeusiv/howdy) are packaged for
openSUSE in the OBS project home:scarabeus_iv:howdy
(https://build.opensuse.org/package/show/home:scarabeus_iv:howdy).
This document is the deployment guide for that package - it is also
shipped in the package itself as README.SUSE - and covers
installation, camera selection, enrolment, PAM activation, testing and
troubleshooting, in the order a deployment actually happens. It follows
a deployment carried out on a system with a Logitech BRIO camera; the
camera node numbers are the part most likely to differ on other
hardware.

## 1. Install the package

Install the main package from the project repository:

    sudo zypper install howdy

The graphical configuration tool is optional:

    sudo zypper install howdy-gtk

The package already ships everything the deployment needs:

- the PAM module and its pam-config definition (activation is a
  separate administrator step, see section 4; the package never
  activates it by itself),
- the SELinux module `howdy_xdm`, installed and loaded by the package
  scriptlets (see section 6),
- the `howdy` group and the models directory /etc/howdy/models in the
  shape 0710 root:howdy, with enrolled model files written 0640
  root:howdy.

No manual SELinux policy work and no chmod/chown on the models
directory are needed or wanted.

Add every user who will enrol a face model to the `howdy` group. Only
users with enrolled models should be members:

    sudo usermod -aG howdy <user>

Group membership takes effect at the user's next login.

## 2. Select the IR camera

Face recognition should use the infrared camera, not the colour one.
List the video devices:

    v4l2-ctl --list-devices

On the Logitech BRIO used for the reference deployment, /dev/video0 is
the colour camera, /dev/video2 is the IR camera, and /dev/video1 and
/dev/video3 are metadata nodes. The IR feed is greyscale, 340x340.
Identify the equivalent node on your hardware instead of copying the
number blindly.

Set the node in /etc/howdy/config.ini, in the [video] section (the
shipped default is `device_path = none`):

    [video]
    device_path = /dev/video2

Confirm the choice:

    sudo howdy test

The test window shows the camera feed. The IR feed looks greyscale and
the IR emitters flash while it runs.

## 3. Enrol a face

Run the enrolment as the user to be enrolled; invoked through sudo,
Howdy enrols the invoking user:

    sudo howdy add

Look straight into the camera when asked. To enrol a different account
as administrator, name it explicitly:

    sudo howdy -U <user> add

List and remove models with:

    sudo howdy list
    sudo howdy remove <id>

The ID is the one shown by `howdy list`. Models are stored in
/etc/howdy/models in the permission shape described in section 1;
there is nothing to adjust there by hand.

## 4. Activate Howdy in PAM

Activate the module in the common PAM stack:

    sudo pam-config --add --howdy

This adds `auth sufficient pam_howdy.so` to /etc/pam.d/common-auth.
Password authentication stays in place as the fall-through whenever
face recognition does not approve a login.

Make sure SSH sessions never attempt face authentication. In
/etc/howdy/config.ini, the [core] section should carry (this is the
shipped default):

    [core]
    abort_if_ssh = true

With it set, pam_howdy detects SSH sessions and skips itself.

## 5. Test in this order

Test each surface separately, in this order:

1. sudo, from a terminal in your graphical session:

       sudo -k whoami

   A face match approves the command; a non-match falls through to the
   password prompt. If sudo does not prompt at all, the account has a
   NOPASSWD rule and sudo never reaches PAM - that says nothing about
   Howdy.

2. The KDE lock screen: lock the session and unlock it. The lock
   screen's PAM stack runs in the user's own context, which is exactly
   why the package ships the models readable by the `howdy` group.
   The user must have logged in again after being added to the group
   (section 1), otherwise the lock screen cannot read the models and
   falls through to the password.

3. The display-manager greeter: log out or reboot, and try face login
   at the greeter. This path additionally depends on the SELinux
   module described in section 6. When this guide was written, the
   greeter path with the packaged fix had not yet had its end-to-end
   cold-boot verification (scheduled for 2026-10-28); the sudo and
   lock-screen paths above were verified.

## 6. Display managers and SELinux

Display managers (SDDM and plasma-login-manager alike) run their PAM
stacks in the SELinux domain `xdm_t`. Under the stock targeted policy,
`xdm_t` may open, read and ioctl V4L2 camera devices, but it may not
mmap them - and capturing a frame mmaps the V4L2 buffers. Face login at
the greeter therefore fails with INVALID_DEVICE ("not possible to open
camera at configured path") while the same setup works in user sessions
(sudo, lock screen), which do not run in `xdm_t`.

The package ships the SELinux module `howdy_xdm`, which grants exactly
that one missing permission (`allow xdm_t v4l_device_t:chr_file map;`),
installs it into the targeted policy and loads it in %post; removing
the package unloads it again. No manual module build, semanage rule or
policy edit is required.

Check that the module is loaded (semodule lives in /usr/sbin, which is
not always on PATH):

    sudo /usr/sbin/semodule -l | grep howdy_xdm

## 7. Optional: exclude TTY logins

The reference deployment keeps face authentication out of the `login`
service (virtual consoles) while leaving it active everywhere else.
That is a local choice, implemented as a per-service PAM override:

1. Copy the vendor service file: `cp /usr/lib/pam.d/login
   /etc/pam.d/login`.
2. In /etc/pam.d/login, replace the single `auth substack common-auth`
   line with the auth lines of /etc/pam.d/common-auth expanded in
   place, minus the `pam_howdy.so` line. Leave the account, password
   and session sections unchanged.

Revert by deleting the override: `sudo rm /etc/pam.d/login`.

Caveat: pam-config manages the common stack, not this override. Once
/etc/pam.d/login exists, later pam-config changes to the common auth
stack do not flow into `login` automatically - re-sync the override by
hand when the common stack changes.

## 8. Troubleshooting

- No face found, or the test feed shows a colour picture: device_path
  points at the colour camera or at a metadata node. Re-check the
  node as in section 2; the IR feed is greyscale.
- All frames black or too dark: the IR emitters flash, so some unlit
  frames are normal and are skipped automatically. If every frame is
  dark, check that the emitter is not covered and that you are within
  camera range; a "camera saw only black frames" message means the IR
  emitter may not be working at all.
- Greeter login fails with INVALID_DEVICE: check that the `howdy_xdm`
  SELinux module is loaded (section 6). If it is missing, reinstall
  the package - do not hand-build policy to work around it.
- Face authentication is attempted in SSH sessions: set
  `abort_if_ssh = true` (section 4).

To disable Howdy again, remove it from the PAM stack:

    sudo pam-config --delete --howdy

Face models and the configuration stay on disk and simply become
inert; the Howdy commands keep working for enrolment management.
