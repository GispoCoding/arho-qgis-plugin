# ARHO platform on UpCloud

OpenTofu root for the shared ARHO platform on UpCloud (plan.md, task 02). It replaces the
AWS configuration in `../infra` once the AWS instances have moved.

Use OpenTofu 1.10 or later (`brew install opentofu`). Terraform is not supported: the lock
file holds OpenTofu registry hashes, the make targets run `tofu`, and the configuration may
use OpenTofu-only features. The language keeps Terraform's names, so the configuration still
has `terraform {}` blocks, `terraform.workspace` and a `.terraform/` folder.

## What it creates

- A router and a private network with DHCP and a default route through the router.
- A NAT gateway for outbound traffic from servers without a public interface.

## Configuration and secrets

Nothing deployment-specific is stored in this public repository. The private arho-deploy
repository has one folder per UpCloud account, `backends/<name>/` (the Gispo account is
`gispo-upcloud`), with:

| File | Contents |
|---|---|
| `backend.hcl` | State bucket and endpoint. Plaintext, no secrets. |
| `credentials.enc.env` | `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` of the Object Storage user `terraform`, and `TF_VAR_state_encryption_passphrase`. sops. |
| `var-files/<workspace>.tfvars.enc.json` | The variables of each platform. sops. |

sops encrypts these with age keys listed in `.sops.yaml` of arho-deploy. The `Makefile` here
decrypts them only while a command runs: the keys into its environment, the variable file
into a temporary file that sops deletes afterwards.

You need sops, age and your own age key in `.sops.yaml` before you can read or write any of
these files, and so before any `make tf-*` command works.

### 1. Install sops and age

sops encrypts and decrypts the files, and has age support built in. The age package is
needed for `age-keygen`, which creates your key.

macOS:

```sh
brew install sops age
```

Linux: install age from the package manager (`sudo apt install age` on Ubuntu 22.04 and
later), and sops from the binaries on its
[releases page](https://github.com/getsops/sops/releases), as it is not in most
distributions:

```sh
SOPS_VERSION=v3.13.3   # check the releases page for the latest
curl -LO "https://github.com/getsops/sops/releases/download/${SOPS_VERSION}/sops-${SOPS_VERSION}.linux.amd64"
sudo install -m 755 "sops-${SOPS_VERSION}.linux.amd64" /usr/local/bin/sops
```

Check both: `sops --version` and `age --version`.

### 2. Add your age key to sops

Everyone has their own age key pair. The private key stays on your machine; only the public
key is shared. Access to the secrets is the list of public keys in `.sops.yaml`.

1. Create your key pair. This prints your public key, `age1...`:

   ```sh
   mkdir -p ~/.config/sops/age
   age-keygen -o ~/.config/sops/age/keys.txt
   ```

   Keep a copy of `keys.txt` in your password manager. If you lose it, you lose access
   until someone adds a new key for you. To see the public key again later, run
   `age-keygen -y ~/.config/sops/age/keys.txt`.

2. Tell sops where the key is. Linux finds `~/.config/sops/age/keys.txt` by itself, but on
   macOS sops looks in `~/Library/Application Support/sops/age/keys.txt`. Add this line to
   your shell profile (`~/.zshrc` or `~/.bashrc`) on either:

   ```sh
   export SOPS_AGE_KEY_FILE="$HOME/.config/sops/age/keys.txt"
   ```

3. Send your public key (`age1...`) to someone who already has access. Never send
   `keys.txt`. They add your key to the `age` list of the backend's rule in
   arho-deploy's `.sops.yaml`, separated by commas, then re-encrypt the existing files for
   the new list from the arho-deploy root and commit:

   ```sh
   for f in backends/gispo-upcloud/credentials.enc.env backends/gispo-upcloud/var-files/*.enc.json; do
     sops updatekeys -y "$f"
   done
   ```

   Changing `.sops.yaml` alone is not enough: it only applies to files created afterwards.
   `updatekeys` needs a key that can already decrypt the files, which is why someone with
   access runs it. The first person, when the rule still has the placeholder, puts in their
   own key before any file is encrypted. Add a second person soon, as files that only one
   key can open are lost with that key.

4. Pull arho-deploy and check that you can decrypt. This prints only "ok", not the secrets:

   ```sh
   cd ../../arho-deploy   # the root of your arho-deploy checkout
   sops -d backends/gispo-upcloud/credentials.enc.env >/dev/null && echo ok
   ```

To remove someone, take their key out of `.sops.yaml`, run `sops updatekeys -y` and
`sops rotate -i` on each file, and change the secrets they could read. The arho-deploy
README has the details.

### 3. Encrypt the files of a new backend

Do this once per backend, after its rule in arho-deploy's `.sops.yaml` has at least one age
key. sops picks the keys from the first rule whose `path_regex` matches the file, so the
files must be under `backends/<name>/`. Run every command from the arho-deploy root:

```sh
cd ../../arho-deploy   # the root of your arho-deploy checkout
```

The examples use the `gispo-upcloud` backend and the `test` workspace.

**The variable file of each workspace.** If a plaintext file exists, encrypt it to the
`.enc.json` name and delete the plaintext:

```sh
sops -e backends/gispo-upcloud/var-files/test.tfvars.json \
  > backends/gispo-upcloud/var-files/test.tfvars.enc.json
rm backends/gispo-upcloud/var-files/test.tfvars.json
```

`make ws=test backend=gispo-upcloud encrypt` in arho-deploy does the same encryption. For a
workspace that has no file yet, create it straight in encrypted form. sops opens your
editor with example content (`"hello": "Welcome to SOPS!..."`); replace all of it with the
variables, save and close. If you close without changes, sops creates no file:

```sh
sops edit backends/gispo-upcloud/var-files/prod.tfvars.enc.json
```

**The backend secrets.** Create `credentials.enc.env` the same way, so the secrets are never
written to disk in plaintext:

```sh
sops edit backends/gispo-upcloud/credentials.enc.env
```

Replace the example content with these three lines, save and close:

```sh
AWS_ACCESS_KEY_ID=<access key of the Object Storage user terraform>
AWS_SECRET_ACCESS_KEY=<secret key of the Object Storage user terraform>
TF_VAR_state_encryption_passphrase=<output of: openssl rand -base64 32>
```

The keys are the ones `bootstrap-state-bucket.sh` printed. Make a new passphrase only for a
backend that has no state yet; for an existing state, use the passphrase it was encrypted
with.

**Check the result.** Each file must list your age key, and no KMS key. A KMS ARN means the
file matched the AWS rule instead, e.g. because it is outside `backends/<name>/`:

```sh
jq '{age: [.sops.age[]?.recipient], kms: [.sops.kms[]?.arn]}' \
  backends/gispo-upcloud/var-files/test.tfvars.enc.json
grep -E '^sops_(age__list_[0-9]+__map_recipient|kms)' backends/gispo-upcloud/credentials.enc.env
```

To check that the secrets decrypt, print only the variable names:

```sh
sops -d backends/gispo-upcloud/credentials.enc.env | cut -d= -f1
sops -d backends/gispo-upcloud/var-files/test.tfvars.enc.json | jq 'keys'
```

**Commit.** `git status` may show only `.sops.yaml`, `backend.hcl` and files ending in
`.enc.json` or `.enc.env` under the backend. `.gitignore` blocks the plaintext names, but
check anyway. Then delete any other plaintext copies of the keys, such as an old
`backend.hcl` with `access_key` lines in new_infra, and run `make tf-init` once, which
rewrites the `.terraform` cache without the keys.

Later changes go through `make edit-vars` and `make edit-credentials`, or `sops edit` on the
file. Never decrypt into a file to edit it.

### UpCloud API token

The UpCloud API token is separate and personal. The provider reads it from `UPCLOUD_TOKEN`
or from the system keyring, where `upctl account login --with-token` saves it.

## Usage

Clone arho-deploy next to this repository, or pass `ARHO_DEPLOY_DIR=<path>` to make.

```sh
make tf-init ws=test backend=gispo-upcloud   # init the backend, select or create the workspace
make tf-plan
make tf-apply
make edit-vars          # edit the variable file of the current workspace
make edit-credentials   # edit the state keys of the current backend
```

### A new UpCloud account

1. Create the state bucket once per account with `./bootstrap-state-bucket.sh` (needs curl,
   jq, openssl and the aws cli). It prints the backend file, the keys and a new passphrase.
2. In arho-deploy, save the backend file as `backends/<name>/backend.hcl`, add an age rule
   for `backends/<name>/` to `.sops.yaml`, and from the arho-deploy root run
   `sops edit backends/<name>/credentials.enc.env` to save the keys and the passphrase.
3. `make tf-init ws=<workspace> backend=<name>`, then `make edit-vars` to create the variable
   file of the workspace.

## Workspaces

Each deployment (test, prod) is a workspace in the same state bucket, stored at
`arho/<workspace>/terraform.tfstate` with its own lock file. The workspace name is also the
environment name in resource names (`arho-<workspace>-*`) and labels, so there is no
`environment` variable. [workspace.tf](workspace.tf) stops a plan in the `default` workspace
and in a workspace whose name is not valid in UpCloud names.

## State encryption

OpenTofu encrypts the state and saved plan files on this machine before they are stored
([encryption.tf](encryption.tf)), so the bucket only holds ciphertext. The key comes from
`TF_VAR_state_encryption_passphrase` in `credentials.enc.env`, one passphrase per backend.
Encryption is enforced: OpenTofu refuses to read or write unencrypted state.

**Losing the passphrase loses the state**, and bucket versioning does not help. Its only
copy is the sops file in arho-deploy, so keep at least two people's age keys on it.
encryption.tf describes how to change the passphrase.

The HashiCorp Terraform extension for VS Code marks the `encryption` block as an error,
because Terraform has no such block. Use the OpenTofu extension instead.

## Open points

- State locking (`use_lockfile`) in UpCloud Object Storage is still to be confirmed: run two
  plans at once and check that the second one waits or fails on the lock.
- The UpCloud provider has no DNS resources, so the DNS zone needs another provider.
- `private_network_cidr` of the test platform is a placeholder until the range is agreed.
