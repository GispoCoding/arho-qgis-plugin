@echo off
set SERVER_ADDRESS=hame-devdb.ctcspesmxrh1.eu-central-1.rds.amazonaws.com
set LOCAL_PORT=5433
set REMOTE_PORT=5432
set LAMBDA_PROXY_HOST=localhost
set LAMBDA_PROXY_PORT=5443
set TUNNEL_USER=ec2-tunnel
set TUNNEL_ADDRESS=hame-dev.bastion.gispocoding.fi
set SSH_KEY_PATH=~/.ssh/id_ed25519

echo Creating SSH tunnel to %SERVER_ADDRESS%:%REMOTE_PORT%...
echo Tunneling local port %LOCAL_PORT% to remote port %REMOTE_PORT%...
echo Setting up SOCKS proxy at %LAMBDA_PROXY_HOST%:%LAMBDA_PROXY_PORT%...

ssh -N  -L %LOCAL_PORT%:%SERVER_ADDRESS%:%REMOTE_PORT% -D %LAMBDA_PROXY_HOST%:%LAMBDA_PROXY_PORT% -i "%SSH_KEY_PATH%" %TUNNEL_USER%@%TUNNEL_ADDRESS%

echo SSH tunnel closed.
pause
