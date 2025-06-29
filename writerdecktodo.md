# 🧾 Writerdeck Integration To-Do for `daily_journal.py`

A list of things to do to integrate daily_journal.py script with a Writerdeck.

## 🧠 System Setup
- [ ] Enable auto-login to terminal (so it boots directly to command line)
- [ ] Set locale and keyboard layout properly (`raspi-config`)
- [ ] Configure screen rotation if needed (Writerdeck is vertical)
- [ ] Disable GUI/Desktop Environment (use Raspbian Lite for speed and lower RAM usage)
- [ ] Disable unused services (e.g. Bluetooth, HDMI, if not needed)
- [ ] Consider read-only root filesystem to prevent SD card wear
- [ ] Set correct timezone for journaling consistency

## ⚙️ Launch Behaviour
- [ ] Auto-launch `daily_journal.py` on boot
  - Option A: Add it to `.bash_profile` or `.bashrc`
  - Option B: Use a `systemd` service for more control
- [ ] Fallback key (e.g. F10) to exit to shell if needed
- [ ] Optional watchdog: restart the journal app if it crashes

## 🗂 File Storage & Backups
- [ ] Create and mount dedicated `/journal` directory
- [ ] Store daily entries in individual files by date
- [ ] Enable optional auto-backup to USB or cloud (when connected)
- [ ] Consider compression or archival of old entries
- [ ] Limit journal directory size (warn or purge if space gets low)

## 🪫 Power Efficiency
- [ ] Lower CPU governor to `powersave`
  ```bash
  echo powersave | sudo tee /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
  ```
- [ ] Disable HDMI output if not needed:
  ```bash
  /usr/bin/tvservice -o
  ```
- [ ] Suspend Wi-Fi or Bluetooth if idle or unused
- [ ] Profile CPU + memory usage periodically (optional)
