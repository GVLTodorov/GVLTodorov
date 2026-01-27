# Transferring a Cursor Authentication Session Between Computers

This guide explains how to manually transfer an authenticated Cursor session from one computer to another by copying its local authentication state.

## When This Is Useful

You may already be logged into Cursor on one machine (e.g. a work computer) and want to use the same session on another device (e.g. a personal laptop) when:

- Re-authentication is blocked by SSO or corporate restrictions
- Temporary credentials are no longer available
- Network or policy limitations prevent logging in again

## How It Works

Cursor stores its authentication state locally in a file called:

```
state.vscdb
```

By copying this file from a machine where Cursor is already authenticated to another machine, you can effectively transfer the active session.

## File Locations by Operating System

Locate `state.vscdb` on the **source machine** (where Cursor is already logged in):

### Linux
```
~/.config/Cursor/User/globalStorage/state.vscdb
```

### macOS
```
~/Library/Application Support/Cursor/User/globalStorage/state.vscdb
```

### Windows
```
%APPDATA%\Cursor\User\globalStorage\state.vscdb
```

## Transferring the Session

1. Close Cursor on both machines.
2. Copy the `state.vscdb` file from the source machine.
3. Paste it into the same path on the target machine.
4. Start Cursor on the target machine.

If successful, Cursor should launch already authenticated.

## Troubleshooting

If the expected path does not exist on the source machine:

- Search the filesystem for `state.vscdb`
- Once found, copy the file
- Recreate the exact directory structure on the target machine before pasting the file

## Important Notes

- This method relies on Cursor’s current local session storage behavior.
- It may stop working if Cursor changes how authentication is handled internally.
- Copying authentication data may violate organizational policies or terms of service.

Use responsibly and at your own risk.
