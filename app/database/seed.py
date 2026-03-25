from app.database.db import SessionLocal
from app.database.models import Ticket, Team, WorkNote
from datetime import datetime, timezone, timedelta

TEAMS = [
    {"name": "Network Team",
     "description": "Handles VPN, WiFi, DNS, firewall, and all network connectivity issues.",
     "handles_categories": "Network",
     "avg_resolution_hours": 4,
     "contact": "network-support@company.com"},
    {"name": "Software Support",
     "description": "Handles application installations, crashes, license errors, and software updates.",
     "handles_categories": "Software",
     "avg_resolution_hours": 6,
     "contact": "software-support@company.com"},
    {"name": "Hardware Support",
     "description": "Handles printers, monitors, keyboards, mice, and physical device issues.",
     "handles_categories": "Hardware",
     "avg_resolution_hours": 8,
     "contact": "hardware-support@company.com"},
    {"name": "Access Management",
     "description": "Handles password resets, account lockouts, permission requests, and MFA issues.",
     "handles_categories": "Access",
     "avg_resolution_hours": 2,
     "contact": "access-mgmt@company.com"},
    {"name": "Email & Collaboration",
     "description": "Handles Outlook, Teams, calendar sync, shared mailboxes, and collaboration tools.",
     "handles_categories": "Email",
     "avg_resolution_hours": 3,
     "contact": "email-support@company.com"},
    {"name": "Security Operations",
     "description": "Handles phishing reports, suspicious logins, ransomware alerts, and security incidents.",
     "handles_categories": "Security",
     "avg_resolution_hours": 1,
     "contact": "secops@company.com"},
]

TICKETS = [
    # ── NETWORK ──────────────────────────────────────────────────────────────
    {
        "ticket_number": "INC0000101",
        "title": "VPN connection fails with error 691",
        "description": "User cannot connect to the corporate VPN. Receives error code 691 — authentication failure. Credentials appear correct.",
        "category": "Network", "priority": "P3", "status": "Resolved",
        "assigned_team": "Network Team",
        "resolution": "User's Active Directory password had expired. Guided user to reset password via self-service portal. VPN connected immediately after reset.",
        "resolution_notes": "1. Confirmed error 691 = auth failure. 2. Checked AD account — password expired. 3. User reset via self-service at password.company.com. 4. VPN tested successfully.",
        "resolution_time_hours": 1,
        "tags": "vpn,error 691,authentication,password,active directory"
    },
    {
        "ticket_number": "INC0000102",
        "title": "Cannot connect to WiFi in Building C",
        "description": "Multiple users on floor 3 of Building C unable to connect to corporate WiFi. Error: cannot obtain IP address.",
        "category": "Network", "priority": "P2", "status": "Resolved",
        "assigned_team": "Network Team",
        "resolution": "DHCP scope for the Building C access point was exhausted. Extended the IP range and flushed stale leases. All users reconnected within 10 minutes.",
        "resolution_notes": "1. Confirmed issue on floor 3 only. 2. Checked DHCP server — scope full. 3. Extended scope from /24 to /23. 4. Ran ipconfig /release and /renew on affected machines.",
        "resolution_time_hours": 2,
        "tags": "wifi,dhcp,ip address,building c,network"
    },
    {
        "ticket_number": "INC0000103",
        "title": "Slow internet speeds affecting entire department",
        "description": "Sales team reporting internet speeds of under 1 Mbps since this morning. Normal speeds should be 100+ Mbps. Affects all browsers and applications.",
        "category": "Network", "priority": "P2", "status": "Resolved",
        "assigned_team": "Network Team",
        "resolution": "A misconfigured QoS policy pushed in yesterday's maintenance window was throttling traffic for the Sales VLAN. Policy was reverted and speeds returned to normal.",
        "resolution_notes": "1. Ran speed tests on multiple machines — confirmed sub-1 Mbps. 2. Reviewed change log — QoS update deployed previous evening. 3. Reverted QoS policy. 4. Confirmed speeds restored.",
        "resolution_time_hours": 3,
        "tags": "slow internet,speed,qos,vlan,sales,bandwidth"
    },
    {
        "ticket_number": "INC0000104",
        "title": "DNS resolution failing for internal sites",
        "description": "User cannot reach internal applications by hostname (e.g., intranet.company.com) but IP addresses work fine.",
        "category": "Network", "priority": "P2", "status": "Resolved",
        "assigned_team": "Network Team",
        "resolution": "User's machine was pointing to an external DNS server instead of internal DNS. Updated DNS settings to point to 10.0.0.1 (internal DNS). All internal sites resolved correctly.",
        "resolution_notes": "1. Pinged intranet.company.com — failed. 2. Pinged by IP — succeeded. 3. Ran ipconfig /all — external DNS 8.8.8.8 set. 4. Updated to 10.0.0.1. 5. Flushed DNS cache.",
        "resolution_time_hours": 1,
        "tags": "dns,internal,hostname,resolution,network settings"
    },
    {
        "ticket_number": "INC0000105",
        "title": "VPN disconnects every 30 minutes",
        "description": "User can connect to VPN but it drops every 30 minutes and requires manual reconnection. This is interrupting work throughout the day.",
        "category": "Network", "priority": "P3", "status": "Resolved",
        "assigned_team": "Network Team",
        "resolution": "VPN client session timeout was set to 30 minutes due to a policy misconfiguration. Updated idle timeout to 8 hours in the VPN gateway profile for the user's group.",
        "resolution_notes": "1. Confirmed 30-min disconnects via VPN logs. 2. Checked gateway timeout policy — set to 1800s. 3. Updated to 28800s (8 hours). 4. User confirmed stable connection.",
        "resolution_time_hours": 2,
        "tags": "vpn,timeout,disconnect,session,idle"
    },

    # ── SOFTWARE ──────────────────────────────────────────────────────────────
    {
        "ticket_number": "INC0000201",
        "title": "Microsoft Office installation fails with error 30015-11",
        "description": "User attempting to install Microsoft 365 from the company portal. Installation starts but fails at 75% with error code 30015-11.",
        "category": "Software", "priority": "P3", "status": "Resolved",
        "assigned_team": "Software Support",
        "resolution": "A remnant of a previous Office installation was conflicting. Ran the Microsoft Support and Recovery Assistant (SaRA) to remove all Office components, then performed a clean install. Completed successfully.",
        "resolution_notes": "1. Confirmed error 30015-11 = install conflict. 2. Downloaded SaRA tool. 3. Ran full Office removal. 4. Restarted machine. 5. Reinstalled M365 — success.",
        "resolution_time_hours": 3,
        "tags": "office,microsoft 365,installation,error 30015,conflict"
    },
    {
        "ticket_number": "INC0000202",
        "title": "Application crashes immediately on launch",
        "description": "SAP client crashes within 2 seconds of launching. No error message — window flashes and disappears. Started happening after Windows update last Tuesday.",
        "category": "Software", "priority": "P2", "status": "Resolved",
        "assigned_team": "Software Support",
        "resolution": "The Windows update KB5034441 introduced a DLL conflict with the SAP GUI version installed. Rolled back the update and deployed SAP GUI patch 7.70 PL5 which is compatible.",
        "resolution_notes": "1. Checked Event Viewer — DLL load failure. 2. Identified conflicting Windows update. 3. Rolled back update via recovery console. 4. Deployed SAP patch. 5. Confirmed stable.",
        "resolution_time_hours": 5,
        "tags": "sap,crash,dll,windows update,conflict,launch"
    },
    {
        "ticket_number": "INC0000203",
        "title": "Software license expired — cannot open application",
        "description": "User receives 'License has expired' message when attempting to open Adobe Acrobat Pro. They need it to complete a contract document today.",
        "category": "Software", "priority": "P3", "status": "Resolved",
        "assigned_team": "Software Support",
        "resolution": "License renewal for the user's Adobe license was missed in the last billing cycle. Purchased a new annual license via Adobe Admin Console and assigned to the user. Application opened within 10 minutes.",
        "resolution_notes": "1. Confirmed license expiry in Adobe Admin Console. 2. Approved emergency purchase request. 3. Purchased and assigned new license. 4. User signed out and back into Adobe — confirmed working.",
        "resolution_time_hours": 2,
        "tags": "adobe,license,expired,acrobat,renewal"
    },
    {
        "ticket_number": "INC0000204",
        "title": "Python environment not found after system reimaging",
        "description": "Developer's laptop was reimaged last week. Python and all installed packages are gone. Needs Python 3.11, pip, and a list of packages restored.",
        "category": "Software", "priority": "P3", "status": "Resolved",
        "assigned_team": "Software Support",
        "resolution": "Installed Python 3.11 via the software portal. User provided requirements.txt — ran pip install -r requirements.txt. Confirmed all packages restored and scripts running.",
        "resolution_notes": "1. Installed Python 3.11 from approved software portal. 2. Added Python to PATH. 3. Installed pip packages from requirements.txt provided by user. 4. Ran test script — success.",
        "resolution_time_hours": 2,
        "tags": "python,pip,packages,reimaging,developer,environment"
    },
    {
        "ticket_number": "INC0000205",
        "title": "Windows update stuck at 35% for 4 hours",
        "description": "Machine has been stuck on the Windows Update screen at 35% since this morning. Cannot use the computer. Tried waiting but no progress.",
        "category": "Software", "priority": "P3", "status": "Resolved",
        "assigned_team": "Software Support",
        "resolution": "Update KB5034441 was causing a known hang issue. Forced restart, booted into safe mode, cleared Windows Update cache (SoftwareDistribution folder), and re-ran updates successfully.",
        "resolution_notes": "1. Forced shutdown after 4 hours stuck. 2. Booted into safe mode. 3. Deleted C:\\Windows\\SoftwareDistribution\\Download. 4. Restarted normally. 5. Updates completed in 20 minutes.",
        "resolution_time_hours": 2,
        "tags": "windows update,stuck,hang,software distribution,kb5034441"
    },

    # ── HARDWARE ─────────────────────────────────────────────────────────────
    {
        "ticket_number": "INC0000301",
        "title": "Printer not found on network — cannot print",
        "description": "User cannot find the floor 2 shared printer (HP LaserJet M404n) when trying to print. Printer was working yesterday. Other users on the floor are also affected.",
        "category": "Hardware", "priority": "P3", "status": "Resolved",
        "assigned_team": "Hardware Support",
        "resolution": "The printer had obtained a new IP address after a DHCP lease renewal. Updated the printer port on the print server to the new IP (192.168.1.87 → 192.168.1.103). All users confirmed printing.",
        "resolution_notes": "1. Confirmed printer offline on print server. 2. Pinged old IP — no response. 3. Checked printer display — new IP shown. 4. Updated port on server. 5. Test print successful.",
        "resolution_time_hours": 1,
        "tags": "printer,network,hp,dhcp,ip address,print server"
    },
    {
        "ticket_number": "INC0000302",
        "title": "Monitor displays no signal after docking station connection",
        "description": "User's external monitor shows 'No Signal' when connected through the Dell docking station. Laptop display works fine. Issue started after new laptop was issued.",
        "category": "Hardware", "priority": "P3", "status": "Resolved",
        "assigned_team": "Hardware Support",
        "resolution": "The new laptop requires a DisplayPort to HDMI adapter (not included). The dock's DisplayPort output was not being detected. Provided the correct adapter — monitor connected and displaying correctly.",
        "resolution_notes": "1. Tested dock with another monitor — same issue. 2. Checked laptop model — requires active DP adapter. 3. Issued DP-to-HDMI active adapter from inventory. 4. Monitor detected immediately.",
        "resolution_time_hours": 2,
        "tags": "monitor,no signal,docking station,displayport,hdmi,adapter"
    },
    {
        "ticket_number": "INC0000303",
        "title": "Keyboard keys not registering correctly",
        "description": "Several keys on user's keyboard produce wrong characters. The 'a' key types '@', the '2' key types a quote mark. Issue is on a physical keyboard, not the laptop keyboard.",
        "category": "Hardware", "priority": "P4", "status": "Resolved",
        "assigned_team": "Hardware Support",
        "resolution": "Keyboard language layout was accidentally changed to UK English. Changed keyboard layout back to US English in Windows language settings. All keys now register correctly.",
        "resolution_notes": "1. Confirmed wrong characters typed. 2. Checked Settings > Language > Keyboard. 3. UK English keyboard was added and set as default. 4. Removed UK layout, set US. 5. Confirmed correct.",
        "resolution_time_hours": 0,
        "tags": "keyboard,wrong characters,language,layout,uk english"
    },
    {
        "ticket_number": "INC0000304",
        "title": "Laptop battery not charging when plugged in",
        "description": "User's laptop shows 'Plugged in, not charging' and battery is at 12%. Has tried different power outlets. The charger is the correct model for the laptop.",
        "category": "Hardware", "priority": "P2", "status": "Resolved",
        "assigned_team": "Hardware Support",
        "resolution": "Battery controller firmware had become corrupted. Performed a battery reset: removed AC adapter, held power for 30 seconds, reconnected AC only (no battery), updated BIOS and battery firmware, then reconnected battery. Charging resumed normally.",
        "resolution_notes": "1. Confirmed correct charger. 2. Tried power cycle — no change. 3. Ran battery diagnostic — firmware error. 4. Performed full battery reset procedure. 5. Updated BIOS. 6. Charging confirmed.",
        "resolution_time_hours": 3,
        "tags": "battery,charging,laptop,firmware,bios,power"
    },

    # ── ACCESS ────────────────────────────────────────────────────────────────
    {
        "ticket_number": "INC0000401",
        "title": "Account locked out — cannot log in",
        "description": "User is locked out of their Windows account. Receives 'Your account has been locked' message. Has tried correct password but still locked.",
        "category": "Access", "priority": "P2", "status": "Resolved",
        "assigned_team": "Access Management",
        "resolution": "Account was locked after 5 failed login attempts (triggered by an old cached password on user's mobile device). Unlocked the account in Active Directory and user updated credentials on all devices.",
        "resolution_notes": "1. Confirmed account locked in AD. 2. Checked audit log — 5 failed attempts from mobile device. 3. Unlocked account in AD Users and Computers. 4. Advised user to update password on mobile. 5. Confirmed login.",
        "resolution_time_hours": 1,
        "tags": "account locked,active directory,password,mobile,lockout"
    },
    {
        "ticket_number": "INC0000402",
        "title": "Cannot access shared drive after department transfer",
        "description": "User transferred from Finance to Marketing 2 weeks ago. Can no longer access the Finance shared drive (which they still need for a transition project) and cannot access the Marketing shared drive yet.",
        "category": "Access", "priority": "P3", "status": "Resolved",
        "assigned_team": "Access Management",
        "resolution": "User's AD group memberships were updated to remove Finance and add Marketing as part of the transfer, but transition access to Finance was not provisioned. Added user to FinanceTransition_ReadOnly group (90-day expiry) and Marketing_General group.",
        "resolution_notes": "1. Checked user's AD groups — only old groups. 2. Confirmed transfer in HR system. 3. Added to Marketing_General group. 4. Added to FinanceTransition_ReadOnly (expires 90 days). 5. Confirmed both drives accessible.",
        "resolution_time_hours": 2,
        "tags": "shared drive,access,permissions,ad groups,department transfer"
    },
    {
        "ticket_number": "INC0000403",
        "title": "MFA not sending verification code",
        "description": "User set up a new phone and can no longer receive the MFA verification code. The old phone is lost. Cannot log into any company systems that require MFA.",
        "category": "Access", "priority": "P2", "status": "Resolved",
        "assigned_team": "Access Management",
        "resolution": "Verified user identity via manager confirmation and employee ID. Reset MFA enrollment in Azure AD. User enrolled new phone in Microsoft Authenticator. MFA working on all systems.",
        "resolution_notes": "1. Verified identity — manager confirmed, checked employee ID. 2. Reset MFA in Azure AD portal. 3. Sent enrollment link to user's personal email (on file). 4. User enrolled new phone. 5. Test login confirmed.",
        "resolution_time_hours": 2,
        "tags": "mfa,multi-factor,authenticator,phone,azure ad,enrollment,reset"
    },
    {
        "ticket_number": "INC0000404",
        "title": "Password reset link expired before use",
        "description": "User requested a password reset link but did not use it in time. The link now shows as expired. Needs to access their account urgently.",
        "category": "Access", "priority": "P3", "status": "Resolved",
        "assigned_team": "Access Management",
        "resolution": "Generated a new password reset link and sent to user's registered recovery email. Password reset links expire after 15 minutes for security. User successfully reset password within 5 minutes of receiving new link.",
        "resolution_notes": "1. Confirmed link expired — 15-min policy. 2. Verified user identity. 3. Generated new reset link via AD admin. 4. Sent to recovery email. 5. User reset within 5 min. 6. Login confirmed.",
        "resolution_time_hours": 1,
        "tags": "password reset,expired,link,recovery,access"
    },
    {
        "ticket_number": "INC0000405",
        "title": "New employee cannot log in on first day",
        "description": "New hire starting today cannot log into their laptop. Receives 'The user name or password is incorrect' message even though IT provided credentials.",
        "category": "Access", "priority": "P2", "status": "Resolved",
        "assigned_team": "Access Management",
        "resolution": "The account was set with 'User must change password at next logon' but the laptop was not connected to the domain when the user first attempted login. Connected laptop to corporate network via Ethernet, ran gpupdate /force, and user was prompted to set a new password successfully.",
        "resolution_notes": "1. Confirmed account active in AD. 2. 'Must change at logon' flag set. 3. Laptop not domain-joined properly over WiFi. 4. Connected via Ethernet. 5. gpupdate /force. 6. User prompted to set password. 7. Login success.",
        "resolution_time_hours": 1,
        "tags": "new hire,first day,login,domain,password,gpupdate"
    },

    # ── EMAIL ─────────────────────────────────────────────────────────────────
    {
        "ticket_number": "INC0000501",
        "title": "Outlook not syncing new emails",
        "description": "User's Outlook shows emails from 3 days ago as the most recent. New emails are visible on Outlook Web App (OWA) but not in the desktop client.",
        "category": "Email", "priority": "P3", "status": "Resolved",
        "assigned_team": "Email & Collaboration",
        "resolution": "Outlook OST cache file had become corrupted. Closed Outlook, renamed the OST file, reopened Outlook which rebuilt the cache from the server. Full sync completed in 15 minutes.",
        "resolution_notes": "1. Confirmed emails visible in OWA — server-side fine. 2. Identified corrupted OST. 3. Closed Outlook. 4. Renamed OST to .old. 5. Reopened Outlook — rebuild started. 6. Sync completed. 7. All emails present.",
        "resolution_time_hours": 1,
        "tags": "outlook,sync,email,ost,cache,corrupt,desktop"
    },
    {
        "ticket_number": "INC0000502",
        "title": "Calendar invites not appearing in Outlook",
        "description": "User is not receiving calendar meeting invitations. Colleagues confirm invites were sent. Invites are visible in OWA but not in the Outlook desktop calendar.",
        "category": "Email", "priority": "P3", "status": "Resolved",
        "assigned_team": "Email & Collaboration",
        "resolution": "The Outlook calendar cache was out of sync. Performed a calendar folder repair using SCANPST.exe on the OST file, then rebuilt the profile. All missing invites appeared after profile rebuild.",
        "resolution_notes": "1. Confirmed invites in OWA. 2. Ran SCANPST on OST — errors found. 3. Repaired file. 4. Still missing — rebuilt full Outlook profile. 5. All invites synced. 6. Tested with a new invite — appeared immediately.",
        "resolution_time_hours": 2,
        "tags": "calendar,invites,outlook,sync,ost,profile,scanpst"
    },
    {
        "ticket_number": "INC0000503",
        "title": "Cannot send emails — error: 550 5.1.1 recipient rejected",
        "description": "User receives bounce-back error '550 5.1.1 The email account that you tried to reach does not exist' when emailing a specific external domain.",
        "category": "Email", "priority": "P3", "status": "Resolved",
        "assigned_team": "Email & Collaboration",
        "resolution": "The recipient's email address had a typo (missing letter). User confirmed the correct address with the external contact. Email sent successfully to the correct address. No server-side issue.",
        "resolution_notes": "1. Checked error — 5.1.1 = address does not exist. 2. Reviewed original email — typo in recipient address. 3. User confirmed correct address with contact. 4. Resent to correct address. 5. Delivered successfully.",
        "resolution_time_hours": 0,
        "tags": "email,bounce,550,recipient,typo,send error"
    },
    {
        "ticket_number": "INC0000504",
        "title": "Shared mailbox not appearing in Outlook",
        "description": "User was given access to a shared mailbox (finance-reports@company.com) by their manager 2 days ago but it does not appear in their Outlook folder list.",
        "category": "Email", "priority": "P3", "status": "Resolved",
        "assigned_team": "Email & Collaboration",
        "resolution": "Permissions had been granted via Exchange but Outlook had not synced the new mailbox. Manually added the shared mailbox via File > Account Settings > Advanced. Mailbox appeared immediately.",
        "resolution_notes": "1. Confirmed permissions granted in Exchange Admin. 2. Restarted Outlook — mailbox not auto-detected. 3. Manually added via account settings > advanced > add mailbox. 4. Mailbox appeared instantly. 5. User confirmed access.",
        "resolution_time_hours": 1,
        "tags": "shared mailbox,outlook,exchange,permissions,add mailbox"
    },

    # ── SECURITY ──────────────────────────────────────────────────────────────
    {
        "ticket_number": "INC0000601",
        "title": "Received suspicious phishing email — possible credentials compromise",
        "description": "User received an email appearing to be from IT asking for their password via a link. User clicked the link but did not enter credentials. Wants to report it and confirm no compromise.",
        "category": "Security", "priority": "P2", "status": "Resolved",
        "assigned_team": "Security Operations",
        "resolution": "Email was confirmed as a phishing attempt targeting the company. Link was analyzed — no credential-harvesting script executed (user did not enter data). User's account was scanned for anomalous activity — none found. Phishing domain reported and blocked at the email gateway. User provided phishing awareness training.",
        "resolution_notes": "1. Isolated phishing email for analysis. 2. Confirmed malicious link in sandboxed browser. 3. No script execution — user did not enter data. 4. Reviewed Azure AD sign-in logs — no anomalies. 5. Blocked domain at gateway. 6. Sent security awareness link to user.",
        "resolution_time_hours": 2,
        "tags": "phishing,email,suspicious,credentials,security,link,clicked"
    },
    {
        "ticket_number": "INC0000602",
        "title": "Suspicious login alert from unrecognized location",
        "description": "User received an email from Azure AD alerting to a sign-in from an unrecognized location (Eastern Europe). User confirms they are in the office in Columbus, OH and did not travel.",
        "category": "Security", "priority": "P1", "status": "Resolved",
        "assigned_team": "Security Operations",
        "resolution": "Confirmed unauthorized access. Immediately revoked all active sessions, forced a password reset, and temporarily disabled the account while investigating. Investigation found credentials were exposed in a third-party breach. Account re-enabled after password reset and MFA reinforcement. Incident report filed.",
        "resolution_notes": "1. Confirmed login from IP in Romania — not user. 2. Revoked all sessions via Azure AD. 3. Disabled account. 4. Forced password reset. 5. Checked HaveIBeenPwned — credentials in breach. 6. Re-enabled account. 7. Enforced MFA. 8. Filed P1 incident report.",
        "resolution_time_hours": 1,
        "tags": "unauthorized login,suspicious,azure ad,breach,password,mfa,security incident,p1"
    },
    {
        "ticket_number": "INC0000603",
        "title": "Ransomware warning popup appearing on machine",
        "description": "User's machine is displaying a popup claiming files have been encrypted and demanding payment in Bitcoin. User has not clicked anything on the popup and immediately called the helpdesk.",
        "category": "Security", "priority": "P1", "status": "Resolved",
        "assigned_team": "Security Operations",
        "resolution": "Machine was immediately isolated from the network. Forensic analysis confirmed ransomware (LockBit variant) had encrypted documents on the local drive and a mapped network share. Machine was wiped and reimaged. Data was restored from last night's backup. Network share was scanned — contained malware was quarantined. Source was a malicious email attachment opened 2 hours prior.",
        "resolution_notes": "1. Immediately isolated machine from network. 2. Engaged SecOps P1 procedure. 3. Confirmed LockBit variant via analysis. 4. Wiped and reimaged machine. 5. Restored from backup (RPO: 24h, data loss: partial). 6. Scanned all network shares. 7. Identified initial vector — email attachment.",
        "resolution_time_hours": 6,
        "tags": "ransomware,lockbit,encryption,p1,critical,bitcoin,backup,restore,network share"
    },
    {
        "ticket_number": "INC0000604",
        "title": "USB drive auto-running unknown software",
        "description": "User plugged in a USB drive found in the parking lot. An application started running automatically. User unplugged it immediately and called the helpdesk.",
        "category": "Security", "priority": "P2", "status": "Resolved",
        "assigned_team": "Security Operations",
        "resolution": "USB contained a baiting malware payload. Endpoint protection caught and quarantined the executable before it could execute fully. Machine was scanned — no persistence found. User was counseled on USB security policy (never plug in unknown USB devices). Incident documented for security awareness training.",
        "resolution_notes": "1. Checked endpoint protection logs — autorun.exe quarantined. 2. Full system scan — no persistence. 3. USB analyzed in sandbox — confirmed malware dropper. 4. No data exfiltration detected. 5. Documented incident. 6. User briefed on USB policy.",
        "resolution_time_hours": 2,
        "tags": "usb,autorun,malware,baiting,security policy,endpoint protection"
    },
    {
        "ticket_number": "INC0000605",
        "title": "Account showing login from multiple countries simultaneously",
        "description": "Security monitoring alerted that user's account logged in from the US and Singapore within 5 minutes of each other — impossible travel scenario.",
        "category": "Security", "priority": "P1", "status": "Resolved",
        "assigned_team": "Security Operations",
        "resolution": "Confirmed impossible travel — account compromised. Suspended account, revoked all tokens, forced password reset, and enabled location-based conditional access policy. Investigation found the Singapore login was a credential stuffing attack. Account restored with enhanced MFA (hardware key required).",
        "resolution_notes": "1. Confirmed impossible travel in Azure AD Identity Protection. 2. Suspended account. 3. Revoked all OAuth tokens. 4. Forced password reset. 5. Added location CA policy. 6. Required hardware FIDO2 key. 7. Account restored. 8. Filed P1 report.",
        "resolution_time_hours": 1,
        "tags": "impossible travel,credential stuffing,account compromise,azure ad,p1,mfa,fido2"
    },

    # ── ACCESS / ENTITLEMENT COMPARISON ──────────────────────────────────────
    {
        "ticket_number": "INC0000701",
        "title": "User lost access to Reporting module — coworkers can access it",
        "description": "User can log into the application but the Reporting module is greyed out and unclickable. Their coworkers on the same team can access it fine. This started after a system update last weekend.",
        "category": "Access", "priority": "P3", "status": "Resolved",
        "assigned_team": "Access Management",
        "resolution": "Compared user's AD group memberships against a working coworker's. User was missing the 'APP_Reports_Viewer' AD group which grants reporting access. The weekend update script had a bug that removed this group from 3 users. Group was re-added and access restored immediately.",
        "resolution_notes": "IMPORTANT: Never re-add AD groups without first verifying the user is entitled to that access.\n1. Confirmed issue is module-specific — user can access all other app areas. 2. Asked user for a coworker's username who has access. 3. Pulled both users' AD group memberships side by side. 4. Identified missing group: APP_Reports_Viewer. 5. Contacted user's manager to confirm user should have reporting access — manager confirmed. 6. Cross-referenced update log — script bug removed group from 4 users. 7. Obtained manager approval for all 4 users before re-adding. 8. Re-added group to approved users only. 9. Confirmed access restored. 10. Flagged update script bug to vendor.",
        "resolution_time_hours": 2,
        "tags": "entitlement,ad group,reporting,module access,comparison,missing group,update bug,manager approval"
    },
    {
        "ticket_number": "INC0000702",
        "title": "Can view records in Salesforce but cannot edit — same role as coworker",
        "description": "User has read-only access in Salesforce. They should have the same permissions as their coworker who can edit records. Both are listed as 'Sales Rep' in the system.",
        "category": "Access", "priority": "P3", "status": "Resolved",
        "assigned_team": "Access Management",
        "resolution": "Both users had the same Salesforce Profile ('Sales Rep') but the affected user was missing a Permission Set ('Edit_Account_Records') that had been manually added to the coworker. After confirming manager approval, the Permission Set was assigned to the user and edit access was confirmed.",
        "resolution_notes": "IMPORTANT: Do not grant any permissions without explicit manager or system admin approval first.\n1. Logged into Salesforce Admin. 2. Compared both users' Profiles — identical. 3. Compared Permission Sets — coworker had Edit_Account_Records, user did not. 4. BEFORE assigning — contacted user's manager (cc'd on ticket) to confirm user is entitled to edit access. Manager confirmed via email. 5. Assigned Edit_Account_Records Permission Set to user. 6. User confirmed edit access restored. 7. Reviewed who else on Sales team is missing this set — found 2 more. 8. Obtained manager approval for those users before applying. 9. Applied to all approved users.",
        "resolution_time_hours": 1,
        "tags": "salesforce,permission set,edit access,read only,entitlement,comparison,profile,manager approval"
    },
    {
        "ticket_number": "INC0000703",
        "title": "Missing approval option in expense system — manager cannot approve team's expenses",
        "description": "Newly promoted manager cannot see the 'Approve' button on their team's expense submissions. Other managers on the same floor have the approve button and use it daily.",
        "category": "Access", "priority": "P2", "status": "Resolved",
        "assigned_team": "Access Management",
        "resolution": "The user's role in the expense system was still set to 'Employee' from before their promotion. The HR system update that triggers role provisioning had not fired. Manually updated role to 'Manager' in the expense system and added them to the Expense_Approvers AD group. Approve button appeared immediately.",
        "resolution_notes": "1. Asked user for a coworker manager's username. 2. Compared roles in expense system — user had 'Employee', coworker had 'Manager'. 3. Checked HR system — promotion was recorded but provisioning job had failed silently. 4. Manually set role to Manager in expense system. 5. Added to Expense_Approvers AD group. 6. Confirmed Approve button visible. 7. Escalated provisioning job failure to HR Systems team.",
        "resolution_time_hours": 2,
        "tags": "expense,approval,manager role,provisioning,entitlement,hr system,role comparison"
    },
    {
        "ticket_number": "INC0000704",
        "title": "SharePoint document library invisible to one user — team can see it",
        "description": "User cannot see a SharePoint document library called 'Finance Contracts' that their entire team uses daily. The library does not appear in the site for this user at all.",
        "category": "Access", "priority": "P3", "status": "Resolved",
        "assigned_team": "Access Management",
        "resolution": "The Finance Contracts library had unique permissions. The user was missing from the Finance_Contracts_Members group. After verifying with the user's manager that they are entitled to this library, the user was added and access was confirmed.",
        "resolution_notes": "IMPORTANT: SharePoint library access for Finance data requires explicit manager approval — do not add without confirmation.\n1. Confirmed user can access the SharePoint site but not the specific library. 2. Checked site permissions — user present. 3. Checked library permissions — library uses unique permissions (broken inheritance). 4. Compared against coworker who has access — coworker in Finance_Contracts_Members group. 5. BEFORE adding user — emailed user's manager and library owner to confirm entitlement. Both confirmed. 6. Added user to Finance_Contracts_Members. 7. Library appeared in user's view. 8. Documented approval in ticket.",
        "resolution_time_hours": 1,
        "tags": "sharepoint,library,permissions,unique permissions,inheritance,entitlement,document library,manager approval"
    },
    {
        "ticket_number": "INC0000705",
        "title": "User cannot see team queue in helpdesk system after promotion to team lead",
        "description": "User was promoted to Team Lead 3 days ago. They can log into the helpdesk system but cannot see the team ticket queue or reassign tickets. Their predecessor could do both.",
        "category": "Access", "priority": "P3", "status": "Resolved",
        "assigned_team": "Access Management",
        "resolution": "User's helpdesk role was still 'Agent'. Team Lead access requires the 'Team_Lead' role plus membership in the team's assignment group. Compared against the previous Team Lead's account. Assigned Team_Lead role and added user to the assignment group. Queue and reassignment controls became visible.",
        "resolution_notes": "IMPORTANT: Role elevation (Agent to Team Lead) requires verification against HR records and manager sign-off before any changes are made.\n1. Asked user for their predecessor's username. 2. Compared roles — user had Agent, predecessor had Team_Lead. 3. Verified promotion in HR system — confirmed. 4. Obtained written approval from user's manager before proceeding. 5. Assigned Team_Lead role in helpdesk admin. 6. Added to L2_Support_Queue assignment group. 7. Confirmed team queue visible and ticket reassignment working. 8. Removed predecessor from Team_Lead role as part of offboarding.",
        "resolution_time_hours": 1,
        "tags": "helpdesk,team lead,queue,role,assignment group,promotion,entitlement comparison"
    },
    {
        "ticket_number": "INC0000706",
        "title": "Application works in the office but not from home via VPN",
        "description": "User can access the internal CRM application when physically in the office but after connecting to VPN from home the application times out. VPN connects successfully and other internal tools work.",
        "category": "Network", "priority": "P3", "status": "Resolved",
        "assigned_team": "Network Team",
        "resolution": "The CRM application runs on a subnet (10.20.5.0/24) that was not included in the VPN split tunnel configuration for standard users. Added the CRM subnet to the split tunnel include list for the user's VPN group policy. Application accessible from home VPN immediately after policy push.",
        "resolution_notes": "1. Confirmed VPN connects — other tools like email work from home. 2. Traced CRM app server IP — on 10.20.5.0/24. 3. Reviewed VPN split tunnel config for user's group — subnet 10.20.5.0/24 not included. 4. Cross-referenced with a user who CAN access CRM from home — they are in a different VPN group with the subnet included. 5. Added 10.20.5.0/24 to standard VPN group tunnel config. 6. Pushed policy update. 7. User confirmed CRM accessible from home.",
        "resolution_time_hours": 2,
        "tags": "vpn,split tunnel,crm,subnet,remote access,home,network policy,routing"
    },
    {
        "ticket_number": "INC0000707",
        "title": "User's Excel shows formula errors — same spreadsheet works for coworker",
        "description": "User opens a shared Excel file and all formulas using commas as separators show errors (e.g. =IF(A1>0,1,0) fails). The same file opens and calculates correctly for everyone else on the team.",
        "category": "Software", "priority": "P4", "status": "Resolved",
        "assigned_team": "Software Support",
        "resolution": "User's Windows regional settings were set to a European locale that uses semicolons as the list separator instead of commas. Excel formula syntax follows the system list separator. Changed regional settings to English (United States) in Control Panel. All formulas resolved correctly after change.",
        "resolution_notes": "1. Confirmed error is formula separator related — IF(A1>0,1,0) fails but IF(A1>0;1;0) works. 2. Checked Windows Settings > Region — user had 'Dutch (Netherlands)' set. 3. Coworker had 'English (United States)'. 4. Changed to English (United States). 5. Reopened Excel — all formulas working. 6. Confirmed with user that no other regional behavior was affected.",
        "resolution_time_hours": 1,
        "tags": "excel,formula,regional settings,locale,separator,comma,semicolon,spreadsheet"
    },
    {
        "ticket_number": "INC0000708",
        "title": "Account keeps locking every morning at 9am — correct password used",
        "description": "User's account locks itself every morning. They reset the password, use it to log in, and by the next morning it is locked again. This has happened 4 days in a row. No unauthorized access is suspected.",
        "category": "Security", "priority": "P2", "status": "Resolved",
        "assigned_team": "Security Operations",
        "resolution": "A scheduled Windows Task on the user's machine was configured to run under their credentials and was failing with the old password each morning, triggering the lockout policy. Identified the task, updated its stored credentials to the new password. Lockouts stopped. User was advised to update stored credentials in all saved locations (Task Scheduler, mapped drives, Credential Manager) when changing passwords.",
        "resolution_notes": "1. Checked AD audit log — lockouts occurring at 09:02 AM daily from the user's own machine. 2. Remoted into machine. 3. Opened Task Scheduler — found 'DailyBackupSync' task running at 9 AM with saved credentials. 4. Task was using old password — generating auth failures and triggering lockout policy (5 attempts). 5. Updated task credentials to current password. 6. Also cleared old credentials from Windows Credential Manager. 7. Monitored next morning — no lockout. 8. Confirmed resolution.",
        "resolution_time_hours": 2,
        "tags": "account lockout,scheduled task,credentials,task scheduler,credential manager,recurring,morning"
    },
    {
        "ticket_number": "INC0000709",
        "title": "User missing from Teams channel after company migration",
        "description": "After the company's migration to a new Microsoft 365 tenant, user cannot find or access the project Teams channel their team uses. Coworkers were migrated and can access it.",
        "category": "Email", "priority": "P3", "status": "Resolved",
        "assigned_team": "Email & Collaboration",
        "resolution": "The bulk migration script processed 847 of 850 users successfully. This user was in a batch that partially failed due to a duplicate UPN conflict. Their Teams memberships were not migrated. Manually added user to the 3 Teams channels they were a member of in the old tenant. User also re-added to relevant SharePoint groups tied to those channels.",
        "resolution_notes": "1. Checked migration log — user's batch showed partial failure (UPN conflict on another user caused batch to partially roll back). 2. Pulled user's old tenant Teams memberships from migration snapshot. 3. Manually added user to all 3 channels in new tenant. 4. Re-added to SharePoint permission groups linked to those channels. 5. Confirmed user can access channels and post messages. 6. Filed bug report with migration vendor.",
        "resolution_time_hours": 3,
        "tags": "teams,migration,m365,channel access,bulk migration,tenant,upn,membership"
    },
    {
        "ticket_number": "INC0000710",
        "title": "New employee can access portal homepage but gets 403 Forbidden on all subpages",
        "description": "New hire joined this week. They can see the company intranet homepage but clicking any link gives a 403 Forbidden error. All other new hires from the same start date have full access.",
        "category": "Access", "priority": "P2", "status": "Resolved",
        "assigned_team": "Access Management",
        "resolution": "The user's account was created in the correct OU but was not added to the 'Intranet_Users' AD security group which grants access beyond the public homepage. All other new hires from that cohort were added via an onboarding script that missed this user due to a blank field in the HR import file. Added user to Intranet_Users group and full portal access was granted within 15 minutes (group policy sync delay).",
        "resolution_notes": "1. Confirmed 403 on all authenticated pages — homepage is public, subpages require group membership. 2. Checked user's AD groups — missing Intranet_Users. 3. Compared against new hire from same start date — they had Intranet_Users. 4. Reviewed onboarding script log — blank 'department' field in HR import caused this user to be skipped. 5. Added to Intranet_Users. 6. Waited 15 min for GP sync. 7. Confirmed full access. 8. Fixed blank field in HR system.",
        "resolution_time_hours": 1,
        "tags": "403,intranet,new hire,onboarding,ad group,security group,access,gp sync"
    },

    # ── ENDPOINT / API ACCESS DENIED ─────────────────────────────────────────
    {
        "ticket_number": "INC0000801",
        "title": "Client receives 403 Access Denied hitting Fund Services API endpoint",
        "description": "Client is calling the Fund Services REST API at /api/v2/funds/balances and receiving a 403 Access Denied response. They are using the correct endpoint URL and their API key. Other clients can hit the same endpoint successfully.",
        "category": "Access", "priority": "P2", "status": "Resolved",
        "assigned_team": "Access Management",
        "resolution": "Client's server IP address (203.45.12.88) was not on the Fund Services API whitelist. The client had recently migrated to a new server and did not submit an IP whitelist request. Opened a sub-ticket with the Fund Services Infrastructure team (INC0000801-SUB) to add the new IP. IP was whitelisted within 2 hours and client confirmed successful API calls.",
        "resolution_notes": "SPECIALIST STEPS:\n1. Ask client to provide the exact error response body — confirm it is 403 (not 401 which is auth, not 404 which is wrong URL).\n2. Ask client to provide their server's outbound IP address (they can check at api.ipify.org).\n3. Log into API Gateway admin console > IP Whitelist > search for client account.\n4. If IP is not present — this is the cause. Do NOT attempt to add it yourself.\n5. ACTION REQUIRED: Open a sub-ticket with Fund Services Infrastructure team. Title: 'IP Whitelist Request — [Client Name]'. Include: client name, account ID, new IP, business justification.\n6. Set your ticket status to 'Pending — External Team' and link the sub-ticket.\n7. Once Fund Services confirms the IP is added, test the endpoint yourself first before closing.\n8. Update ticket with resolution and close.",
        "resolution_time_hours": 3,
        "tags": "403,api,fund services,ip whitelist,access denied,endpoint,sub-ticket,infrastructure"
    },
    {
        "ticket_number": "INC0000802",
        "title": "API endpoint returns 401 Unauthorized — credentials appear correct",
        "description": "Developer is receiving 401 Unauthorized on the payment processing API. They are sending a username and password in the request header. The credentials match what was provisioned in the welcome email.",
        "category": "Access", "priority": "P2", "status": "Resolved",
        "assigned_team": "Access Management",
        "resolution": "The API uses API Key authentication, not Basic Auth username/password. The client was sending credentials in the wrong format. The correct method is to pass the API key in the Authorization header as 'Bearer {api_key}'. Once the developer updated their request format, the 401 was resolved. Additionally, the welcome email was updated to include the correct authentication format.",
        "resolution_notes": "SPECIALIST STEPS:\n1. Confirm the exact error — 401 means authentication failure (wrong credentials OR wrong auth method), not authorization.\n2. Ask developer to share their request headers (redact the actual key value — just confirm the header name and format).\n3. Check API documentation for the correct auth method: Basic Auth vs Bearer Token vs API Key in header vs query param.\n4. Common mistake: sending username/password when API expects 'Authorization: Bearer {key}'.\n5. If credentials are correct format but still 401 — check if account is active in API management portal.\n6. If account is locked or expired — open sub-ticket with API Platform team to reset credentials.\n7. If none of the above — escalate to API Platform team as potential backend auth issue.",
        "resolution_time_hours": 1,
        "tags": "401,unauthorized,api,authentication,bearer token,api key,credentials,wrong format"
    },
    {
        "ticket_number": "INC0000803",
        "title": "Access Denied on internal portal — works without VPN, fails with VPN connected",
        "description": "User can access the vendor management portal fine when off VPN but receives an Access Denied error the moment they connect to the corporate VPN. Issue started this week and is affecting multiple users.",
        "category": "Network", "priority": "P2", "status": "Resolved",
        "assigned_team": "Network Team",
        "resolution": "The vendor management portal is hosted externally and has an IP whitelist. When users connect to VPN, their outbound traffic routes through the corporate proxy (10.0.1.5) and exits via the corporate IP (198.51.100.45). The vendor had recently updated their IP whitelist and accidentally removed the corporate proxy IP. Opened a sub-ticket with the Network team to confirm the corporate egress IP, then contacted the vendor to re-add it. Issue resolved for all users.",
        "resolution_notes": "SPECIALIST STEPS:\n1. Confirm the issue is VPN-specific — ask user to test with VPN off. If works off VPN, root cause is the traffic routing change VPN introduces.\n2. When on VPN, traffic exits via corporate egress IP, not user's home IP. The external vendor sees corporate IP.\n3. ACTION: Open sub-ticket with Network team requesting the current corporate egress IP address.\n4. Contact the external vendor's support with: corporate egress IP, date issue started, affected user count.\n5. Request vendor re-add the corporate IP to their whitelist.\n6. Set ticket to 'Pending — Vendor' while awaiting their update.\n7. Once vendor confirms update, test from VPN — confirm with 2-3 affected users.\n8. Note: if vendor cannot be reached, Network team can investigate whether a proxy bypass rule is an interim option.",
        "resolution_time_hours": 4,
        "tags": "vpn,access denied,whitelist,egress ip,corporate proxy,vendor,external portal,routing"
    },
    {
        "ticket_number": "INC0000804",
        "title": "Client API key stopped working overnight — was working yesterday",
        "description": "Client reports their API integration stopped working at midnight with a 401 error. No code changes were made. The same API key was working fine the day before. Affects their automated overnight batch process.",
        "category": "Access", "priority": "P1", "status": "Resolved",
        "assigned_team": "Access Management",
        "resolution": "The client's API key had a 90-day expiration policy. The key was provisioned 90 days ago and expired at midnight automatically. The client was not notified because their account did not have an admin email configured for expiry alerts. Generated a new API key, delivered it securely via the client portal, and configured their account with an admin email for future expiry warnings 14 days in advance.",
        "resolution_notes": "SPECIALIST STEPS:\n1. Confirm 401 error — get exact timestamp when it started (midnight = strong signal of scheduled expiry).\n2. Log into API management portal > Client Accounts > find client > view API Keys.\n3. Check key status — look for 'Expired' status and expiry date/time.\n4. If expired — do NOT reactivate old key. Generate a new key.\n5. Deliver new key ONLY via secure channel — client portal message or encrypted email. Never send in plain email or chat.\n6. Ask client to update their integration and test.\n7. Check client account for admin email — if missing, add it and configure expiry alerts.\n8. Mark as P1 because automated batch processes failing overnight = business impact.\n9. Note in ticket: recommend client implement key rotation monitoring in their own system.",
        "resolution_time_hours": 2,
        "tags": "api key,expired,401,midnight,batch process,rotation,p1,expiry policy,automated"
    },
    {
        "ticket_number": "INC0000805",
        "title": "User gets Access Denied on fund services portal — other team members have access",
        "description": "User needs to access the Fund Services client portal to view fund statements. When they attempt to log in they receive 'Access Denied — You are not authorized to access this application'. Their manager and 3 teammates can log in without issues.",
        "category": "Access", "priority": "P3", "status": "Resolved",
        "assigned_team": "Access Management",
        "resolution": "Fund Services portal uses a separate identity system — access is provisioned by the Fund Services team, not IT. The user had never been provisioned in the Fund Services system. IT does not have admin rights to this external portal. Opened an access request ticket with the Fund Services team (INC0000805-SUB) on the user's behalf, providing manager approval. Fund Services provisioned the account within 4 hours.",
        "resolution_notes": "SPECIALIST STEPS:\n1. Confirm whether this is an IT-managed system or a third-party/vendor system.\n2. For Fund Services portal — IT does NOT manage provisioning. This requires a sub-ticket to the Fund Services team.\n3. Collect required information before opening sub-ticket: user's full name, employee ID, email, manager name, business justification, access level needed (read-only vs. full access).\n4. Get explicit manager approval via email — attach to sub-ticket.\n5. ACTION: Open sub-ticket to Fund Services team. Template: 'Access Provisioning Request — Fund Services Portal — [User Name]'.\n6. Set your ticket to 'Pending — Fund Services' and link the sub-ticket.\n7. SLA for Fund Services provisioning: 4 business hours for standard, 1 hour for P1.\n8. Once user confirms access — close your ticket. Do not close until user has tested login.",
        "resolution_time_hours": 5,
        "tags": "fund services,access denied,provisioning,external system,sub-ticket,manager approval,third party"
    },
    {
        "ticket_number": "INC0000806",
        "title": "Firewall blocking access to third-party data feed endpoint",
        "description": "Developer's application cannot reach an external data feed at https://datafeed.vendor.com:8443. Receives a connection timeout, not an HTTP error. The endpoint works when tested from a personal laptop on home WiFi but not from the corporate network.",
        "category": "Network", "priority": "P2", "status": "Resolved",
        "assigned_team": "Network Team",
        "resolution": "The corporate firewall blocks all non-standard outbound ports by default. Port 8443 was not in the approved outbound allow list. Opened a firewall rule request with the Network team providing the destination IP, port, and business justification. Network team added the rule within 2 hours. Developer confirmed connectivity from corporate network.",
        "resolution_notes": "SPECIALIST STEPS:\n1. Key diagnostic: connection timeout (not 403/401) on corporate network but works on home WiFi = firewall block, not auth issue.\n2. Ask developer to run: telnet datafeed.vendor.com 8443 — if it hangs with no response, port is blocked.\n3. Standard ports (80, 443) are allowed. Non-standard ports (8443, 8080, custom) require explicit firewall rules.\n4. ACTION: Open sub-ticket with Network team for firewall rule request. Include: destination hostname, destination IP, port number, protocol (TCP/UDP), business justification, application name, data classification.\n5. Network team SLA for firewall rule requests: 4 hours for standard, same-day for P1.\n6. Set your ticket to 'Pending — Network Team'.\n7. Once rule is added, have developer test telnet first, then the full application.\n8. Document the approved rule number in your ticket for audit trail.",
        "resolution_time_hours": 3,
        "tags": "firewall,port blocked,8443,connection timeout,corporate network,outbound rule,network team,sub-ticket"
    },
    {
        "ticket_number": "INC0000807",
        "title": "SSL certificate error when accessing internal API endpoint",
        "description": "Application team receives SSL handshake error when calling an internal API: 'SSL: CERTIFICATE_VERIFY_FAILED'. The endpoint was working last week. Other teams calling the same endpoint report the same issue starting Monday.",
        "category": "Software", "priority": "P1", "status": "Resolved",
        "assigned_team": "Software Support",
        "resolution": "The internal API's SSL certificate expired on Sunday night. The certificate renewal process had failed silently 30 days prior due to a misconfigured renewal job. The certificate was renewed and deployed by the Infrastructure team (sub-ticket INC0000807-SUB) within 90 minutes. All calling applications confirmed resolution.",
        "resolution_notes": "SPECIALIST STEPS:\n1. SSL_CERTIFICATE_VERIFY_FAILED = expired or untrusted certificate. This is NOT an application bug.\n2. Confirm it is affecting multiple teams — if yes, this is infrastructure-level and P1.\n3. Immediately escalate to P1. Multiple teams blocked = critical business impact.\n4. ACTION: Open sub-ticket with Infrastructure/Platform team. Title: 'URGENT — SSL Certificate Expired on [endpoint]'. Include endpoint URL, error message, number of affected teams.\n5. Do NOT ask application teams to disable SSL verification as a workaround — this is a security risk and should never be done in production.\n6. Set your ticket status to 'In Progress — Infrastructure Team'.\n7. Infrastructure team will renew and deploy the certificate.\n8. After fix, ask all affected teams to test and confirm before closing.\n9. Follow up with Infrastructure on why auto-renewal failed — document in ticket.",
        "resolution_time_hours": 2,
        "tags": "ssl,certificate,expired,handshake,p1,infrastructure,sub-ticket,api,tls"
    },
    {
        "ticket_number": "INC0000808",
        "title": "Rate limit exceeded error hitting payment API — 429 Too Many Requests",
        "description": "Client integration is receiving 429 Too Many Requests errors from the payment processing API. This started after they expanded their customer base. Their contract allows API access but they are hitting errors during peak hours.",
        "category": "Software", "priority": "P3", "status": "Resolved",
        "assigned_team": "Software Support",
        "resolution": "Client's API tier (Standard) has a rate limit of 100 requests/minute. Their expanded traffic was exceeding this during peak hours. Two options were presented: (1) upgrade to Premium tier (500 req/min) or (2) implement exponential backoff and request queuing on their side. Client chose to upgrade. Opened sub-ticket with API Platform team to upgrade client's tier. Additionally shared rate limiting best practices and retry logic documentation with the client.",
        "resolution_notes": "SPECIALIST STEPS:\n1. 429 = rate limit exceeded. Check client's current API tier and rate limit in the API management portal.\n2. Pull rate limit metrics for the client — identify peak usage times and how far over the limit they are.\n3. Present two options to client: a) Upgrade API tier (costs more, immediate fix), b) Implement backoff/retry logic (free, requires their dev work).\n4. If client wants tier upgrade — ACTION: open sub-ticket with API Platform team with client account ID and desired tier.\n5. If client implements backoff — share retry documentation and recommended algorithm (exponential backoff with jitter).\n6. Do not modify rate limits directly — this requires API Platform team approval.\n7. Set reasonable expectations: tier upgrade typically takes 1 business day to activate.\n8. Monitor for 24 hours after fix and confirm 429s have stopped.",
        "resolution_time_hours": 4,
        "tags": "429,rate limit,too many requests,api tier,upgrade,backoff,retry,payment api,throttle"
    },
]

def seed_if_empty():
    db = SessionLocal()
    try:
        if db.query(Team).count() > 0:
            return
        print("  Seeding database with teams and tickets...")
        for t in TEAMS:
            db.add(Team(**t))
        db.commit()
        for t in TICKETS:
            db.add(Ticket(**t))
        db.commit()
        print(f"  Seeded {len(TEAMS)} teams and {len(TICKETS)} tickets.")
    finally:
        db.close()


WORK_NOTE_SEEDS = {
    "INC0000805": [
        {"note_type": "investigation", "author": "J. Rivera",
         "content": "User confirmed the error message is 'Access Denied — You are not authorized to access this application'. Attempted password reset — did not resolve. Checked AD account — active and not locked. This does not appear to be an IT-managed system.",
         "offset_minutes": 0},
        {"note_type": "comment", "author": "J. Rivera",
         "content": "Confirmed with the user that their manager and 3 teammates all have access. Reached out to the manager (cc'd on ticket) to verify user is entitled to this access and to provide business justification for the request.",
         "offset_minutes": 15},
        {"note_type": "comment", "author": "J. Rivera",
         "content": "Manager responded via email — confirmed user is entitled to Fund Services access (read-only, same as team). Attached approval to ticket. Opening sub-ticket to Fund Services team now.",
         "offset_minutes": 35},
        {"note_type": "workaround", "author": "J. Rivera",
         "content": "Sub-ticket INC0000805-SUB opened with Fund Services team. Subject: 'Access Provisioning Request — Fund Services Portal — [User Name]'. Provided employee ID, email, manager name, and attached manager approval. Set ticket status to Pending — Fund Services.",
         "offset_minutes": 45},
        {"note_type": "comment", "author": "J. Rivera",
         "content": "Fund Services team confirmed account provisioned. User tested login — access confirmed working. Closing ticket.",
         "offset_minutes": 300},
    ],
    "INC0000702": [
        {"note_type": "investigation", "author": "M. Chen",
         "content": "User reports read-only access in Salesforce despite having the same 'Sales Rep' role as coworker who can edit. Logged into Salesforce Admin to begin comparison.",
         "offset_minutes": 0},
        {"note_type": "investigation", "author": "M. Chen",
         "content": "Compared Profiles: both users have 'Standard Sales Rep' profile — identical. Difference found in Permission Sets: coworker has 'Edit_Account_Records' assigned, user does not. This is the likely cause.",
         "offset_minutes": 20},
        {"note_type": "pending_response", "author": "M. Chen",
         "content": "IMPORTANT: Before assigning any Permission Sets, emailed user's manager to confirm user is entitled to edit access. Set ticket to Pending — Manager Approval. Will not proceed until confirmation received.",
         "offset_minutes": 25},
        {"note_type": "comment", "author": "M. Chen",
         "content": "Manager confirmed via email — user is entitled to full Sales Rep edit permissions. Assigned 'Edit_Account_Records' Permission Set. User tested and confirmed edit access is now working.",
         "offset_minutes": 55},
        {"note_type": "comment", "author": "M. Chen",
         "content": "Proactively checked the rest of the Sales team — found 2 additional users missing the same Permission Set. Sent manager approval request for those users before applying any changes.",
         "offset_minutes": 60},
    ],
    "INC0000601": [
        {"note_type": "investigation", "author": "S. Okafor",
         "content": "User forwarded suspicious email. Sender appears to be 'IT-Support@company-helpdesk.net' (NOT our domain). Email claims user's account will be locked unless they click a link and verify credentials. Classic phishing indicators: urgency, off-domain sender, credential request.",
         "offset_minutes": 0},
        {"note_type": "investigation", "author": "S. Okafor",
         "content": "Checked email headers — originating IP is 185.220.x.x (known Tor exit node). Link in email resolves to a credential harvesting page mimicking our internal portal. User has NOT clicked the link — confirmed.",
         "offset_minutes": 10},
        {"note_type": "comment", "author": "S. Okafor",
         "content": "Submitted phishing URL to our threat intel platform for blocking. Notified Email Security team to add sender domain to blocklist and deploy retroactive scan across all mailboxes for same sender.",
         "offset_minutes": 20},
        {"note_type": "comment", "author": "S. Okafor",
         "content": "Email Security confirmed 14 other employees received the same email. None clicked the link. Sender domain blocked. Retroactive scan complete. Filing security awareness reminder to all staff.",
         "offset_minutes": 45},
    ],
    "INC0000803": [
        {"note_type": "investigation", "author": "T. Nguyen",
         "content": "Reproduced the issue — portal is accessible without VPN, Access Denied with VPN connected. This is affecting at least 4 users on the same team. Issue started Monday morning.",
         "offset_minutes": 0},
        {"note_type": "investigation", "author": "T. Nguyen",
         "content": "When on VPN, traffic routes through corporate proxy 10.0.1.5 and exits via our corporate egress IP. The vendor portal is external and appears to have an IP whitelist. Opening sub-ticket with Network team to get the current corporate egress IP.",
         "offset_minutes": 15},
        {"note_type": "workaround", "author": "T. Nguyen",
         "content": "Sub-ticket opened with Network team. Network team confirmed egress IP: 198.51.100.45. Contacted vendor support via their portal with: egress IP, date issue started, 4 affected users. Vendor is investigating their whitelist. Ticket set to Pending — Vendor.",
         "offset_minutes": 40},
        {"note_type": "comment", "author": "T. Nguyen",
         "content": "Vendor confirmed their team accidentally removed our corporate IP during a whitelist audit on Sunday. IP re-added. Tested with 3 affected users — all confirmed access restored.",
         "offset_minutes": 240},
    ],
    "INC0000701": [
        {"note_type": "investigation", "author": "A. Patel",
         "content": "User can access all other areas of the application — only the Reporting module is greyed out. Issue started after the weekend system update. Asking user to provide a coworker's username who still has reporting access.",
         "offset_minutes": 0},
        {"note_type": "investigation", "author": "A. Patel",
         "content": "Pulled both users' AD group memberships side by side. User is missing: APP_Reports_Viewer. Coworker has it. This group is what grants reporting access. Checking the weekend update log.",
         "offset_minutes": 20},
        {"note_type": "investigation", "author": "A. Patel",
         "content": "Found the cause — update script had a bug that removed APP_Reports_Viewer from 4 users. Before taking any action, contacting all affected users' managers to confirm they are still entitled to reporting access.",
         "offset_minutes": 35},
        {"note_type": "comment", "author": "A. Patel",
         "content": "All 4 managers confirmed entitlement. Re-added APP_Reports_Viewer group to approved users only. All 4 users confirmed reporting access restored. Flagged update script bug to vendor with a reproduction report.",
         "offset_minutes": 60},
    ],
}


def seed_work_notes_if_empty():
    db = SessionLocal()
    try:
        if db.query(WorkNote).count() > 0:
            return
        print("  Seeding work notes...")
        base_time = datetime.now(timezone.utc) - timedelta(hours=48)
        count = 0
        for ticket_number, notes in WORK_NOTE_SEEDS.items():
            ticket = db.query(Ticket).filter(Ticket.ticket_number == ticket_number).first()
            if not ticket:
                continue
            for note in notes:
                ts = base_time + timedelta(minutes=note["offset_minutes"])
                db.add(WorkNote(
                    ticket_id=ticket.id,
                    note_type=note["note_type"],
                    author=note["author"],
                    content=note["content"],
                    created_at=ts,
                ))
                count += 1
        db.commit()
        print(f"  Seeded {count} work notes across {len(WORK_NOTE_SEEDS)} tickets.")
    finally:
        db.close()
