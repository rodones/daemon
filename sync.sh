#!/usr/bin/env bash
# shellcheck disable=SC2029

source sync.env

if [ "$1" != "--skip" ]; then
    echo "> stopping service..."
    ssh $REMOTE_USER@$REMOTE_HOST "cd $REMOTE_PATH && make pre-update"
fi

echo "> updating source code..."
rsync \
    --delete \
    --verbose \
    --include ".env" \
    --exclude-from ".gitignore" \
    --exclude ".venv" \
    --exclude ".git" \
    --exclude ".vscode" \
    --exclude ".flake8" \
    --rsync-path="sudo rsync" \
    -aze "ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no" \
    . "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"

if [ "$1" != "--skip" ]; then
    echo "> starting service..."
    ssh $REMOTE_USER@$REMOTE_HOST "cd $REMOTE_PATH && make post-update"
fi
