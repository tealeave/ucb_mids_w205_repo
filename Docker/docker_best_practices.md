Here’s a set of best practices and workflows to keep your images lean, your containers tidy, and your development environment reproducible:

---

## 1. Building & Tagging Images

* **Use explicit tags**

  ```bash
  docker build -f Dockerfile -t w205-dev:latest .
  ```

  This makes it easy to refer to “latest” for day-to-day work, but pin to a specific tag or digest (`w205-dev:v1.2.3` or `@sha256:…`) when you need immutability.

* **Keep Dockerfiles small and layered**

  * Install only what you need in each layer.
  * Clean up `apt-get` caches (e.g. `rm -rf /var/lib/apt/lists/*`) in the same `RUN` that installs packages.
  * Use multi-stage builds to remove build-time dependencies.

* **Rebuild only when necessary**

  * If you haven’t changed your Dockerfile (or upstream base image), you can skip rebuilds—Docker’s layer cache will reuse existing layers.
  * Use `docker image inspect w205-dev` (or `docker images`) to verify your local image exists before rebuilding.

---

## 2. Running Containers

* **Ephemeral vs. persistent**

  * **Ephemeral**:

    ```bash
    docker run --rm -it w205-dev bash
    ```

    `--rm` means the container’s writable layer is automatically deleted on exit—great for one-off tests.
  * **Persistent** (for day-to-day dev):

    ```bash
    docker run -d --name dev-w205 \
      -v "$PWD":/workspaces/w205 \
      -w /workspaces/w205 \
      -u w205 \
      w205-dev \
      tail -f /dev/null
    ```

    You `docker exec -it dev-w205 bash` into it, and it doesn’t go away on exit.

* **Mount your code & data**

  * Always bind-mount (`-v`) your project directory so code changes live on the host and aren’t baked into the image’s layer (so you don’t have to rebuild to see your edits).
  * For databases or other mutable state you want to persist, use named volumes:

    ```yaml
    volumes:
      pgdata:
    services:
      postgres:
        image: postgres
        volumes:
          - pgdata:/var/lib/postgresql/data
    ```

* **Stop & remove when done**

  ```bash
  docker stop dev-w205
  docker rm   dev-w205
  ```

  Or combine with force:

  ```bash
  docker rm -f dev-w205
  ```

---

## 3. Cleaning Up Disk Usage

Docker images, containers, volumes, and build cache can accumulate. Use these commands periodically:

* **Remove dangling (“\<none>”) images**

  ```bash
  docker image prune -f
  ```
* **Remove unused images (not referenced by any container)**

  ```bash
  docker image prune -a -f
  ```
* **Remove stopped containers**

  ```bash
  docker container prune -f
  ```
* **Remove unused volumes**

  ```bash
  docker volume prune -f
  ```
* **Full system cleanup**

  ```bash
  docker system prune -a --volumes -f
  ```
* **Clean up build cache**

  ```bash
  docker builder prune -a -f
  ```

> **Tip:** You can automate this with a cron job or run these commands interactively whenever you see disk usage growing.

---

## 4. Persisting Your Dev-Env Changes

You often want to install new tools inside your dev container (e.g. `pip install`, `npm install -g`, adding system packages) and keep them around:

1. **Preferred: Bake changes into your Dockerfile**

   * Add the package installs to your Dockerfile, then rebuild.
   * Keeps your environment reproducible (“Infrastructure as Code”).

2. **Quick & Dirty: Commit a container snapshot**

   ```bash
   docker commit dev-w205 myregistry/w205-dev:with-extras
   ```

   * Creates a new image layer capturing your current container state.
   * You can then run new containers from that image.
   * **But** it’s opaque—best for temporary snapshots, not long-term.

3. **Volumes for config & data**

   * Use named volumes (or host-binds) for things like database data, log files, or your home directory inside the container (`-v dev-home:/home/w205`) so installing fonts or dotfiles survives container recreation.

---

## 5. Example Day-to-Day Workflow

```bash
# --- morning: bring up your dev container (reuses existing image & container) ---
docker start dev-w205 2>/dev/null || \
docker run -d --name dev-w205 \
  -v "$PWD":/workspaces/w205 \
  -w /workspaces/w205 \
  -u w205 \
  w205-dev \
  tail -f /dev/null

# get a shell
docker exec -it dev-w205 bash

# --- install a new tool inside the container ---
# (you could instead add this to Dockerfile and rebuild)
pip install black

# --- at end of day: stop container ---
exit          # leaves your shell
docker stop dev-w205

# --- on disk cleanup (run weekly/monthly) ---
docker system prune -a --volumes -f
docker builder prune -a -f
```

With this approach you:

* Keep your **image** small and stable.
* Mount your **code** so edits don’t require rebuilds.
* Stop containers when idle so they don’t consume memory/CPU.
* Periodically prune unused artifacts to reclaim disk.
* Persist development tools either declaratively (Dockerfile) or via volumes/commits.
