@echo off
set DB_SERVER_ADDRESS=hame-devdb.ctcspesmxrh1.eu-central-1.rds.amazonaws.com
set DB_LOCAL_PORT=5433
set DB_REMOTE_PORT=5432
set API_SERVER_ADDRESS=kfhh24yii6.execute-api.eu-central-1.amazonaws.com
set API_LOCAL_PORT=5443
set API_REMOTE_PORT=443
set TUNNEL_USER=ec2-tunnel
set TUNNEL_ADDRESS=hame-dev.bastion.gispocoding.fi
set SSH_KEY_PATH=~/.ssh/id_ed25519

echo Creating SSH tunnel to %DB_SERVER_ADDRESS%:%DB_REMOTE_PORT% and %API_SERVER_ADDRESS%:%API_REMOTE_PORT%...
echo Tunneling local port %DB_LOCAL_PORT% to remote port %DB_REMOTE_PORT%...
echo Tunneling local port %API_LOCAL_PORT% to remote port %API_REMOTE_PORT%...

ssh -N  -L %DB_LOCAL_PORT%:%DB_SERVER_ADDRESS%:%DB_REMOTE_PORT%  -L %API_LOCAL_PORT%:%API_SERVER_ADDRESS%:%API_REMOTE_PORT% -i "%SSH_KEY_PATH%" %TUNNEL_USER%@%TUNNEL_ADDRESS%

echo SSH tunnel closed.
pause
