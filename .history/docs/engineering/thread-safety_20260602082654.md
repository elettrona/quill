# Thread-safety invariants

This note documents the concurrency invariants for Quill's module-level and
shared caches (CQ-17). It is the canonical reference for how the lazily-loaded
caches stay correct when several threads touch them at once — the writing thread,
the file-I/O and compute pools, and watch-folder worker threads.

## Concurrency model recap

- The UI thread owns the wxPython widgets and the editor buffer.
- File I/O and heavier compute run on worker threads / thread pools.
- Cross-thread UI updates marshal back through `wx.CallAfter` / `wx.CallLater`.

Because a lazily-loaded cache can be touched from more than one of these threads
on first use, each such cache is guarded by a lock. There are no unguarded
module-level mutable caches in `quill/core`.

## Pattern 1 — module-level lazy caches (double-checked locking)

Read-mostly data that is expensive to build once and then never changes uses a
module-level `threading.Lock` plus double-checked locking: an unlocked fast-path
read of the cached value, then the lock, a re-check, and population under the
lock. The cached value is always an immutable snapshot (a `frozenset`, or a dict
that is never mutated after publication), so readers that win the fast path never
observe a half-built structure.

| Cache | Module | Lock | Cached state |
| --- | --- | --- | --- |
| Word-list fallback | [quill/core/spellcheck.py](../../quill/core/spellcheck.py) | `_BACKEND_LOCK` | `_WORDLIST_CACHE` (`frozenset`) |
| Enchant dictionary handle | [quill/core/spellcheck.py](../../quill/core/spellcheck.py) | `_BACKEND_LOCK` | `_ENCHANT_DICT`, `_ENCHANT_TRIED` |
| Thesaurus index | [quill/core/thesaurus.py](../../quill/core/thesaurus.py) | `_LOAD_LOCK` | `_INDEX` (dict, never mutated after build), `_LOAD_ERROR` |

Invariants for this pattern:

1. The cache slot is only ever written while holding the lock.
2. Once published, the cached object is treated as immutable. To refresh it,
   replace the whole slot under the lock; never mutate in place.
3. The fast-path read outside the lock is safe because it reads a single
   reference that is either `None` (not yet built) or a fully-built snapshot.
4. A failed load still publishes a definitive result (an empty cache plus an
   error string) so the expensive attempt is not retried on every call.

## Pattern 2 — per-instance mutable-set caches

Caches that are genuinely mutated over time hold a per-instance
`threading.Lock` and take it around every read and write of the shared mutable
state.

| Cache | Module | Lock | Shared state |
| --- | --- | --- | --- |
| Watch-folder seen-set | [quill/core/watch_folder.py](../../quill/core/watch_folder.py) | `self._lock` | `self._seen_files` (`set[str]`) |

Invariants for this pattern:

1. Every access to the mutable set — `clear`, membership test, and `add` — is
   performed inside `with self._lock`.
2. The lock is held only for the brief set operation, never across slow work
   such as file I/O or dispatching an action, so worker threads do not serialise
   behind each other.

## Stability helpers

The stability layer follows the same per-instance discipline: the task manager
([quill/stability/task_manager.py](../../quill/stability/task_manager.py)), the
wx dispatch queue ([quill/stability/wx_dispatch.py](../../quill/stability/wx_dispatch.py)),
and the heartbeat ([quill/stability/wx_heartbeat.py](../../quill/stability/wx_heartbeat.py))
each own a `threading.Lock` and take it around their shared bookkeeping.

## Rule for new caches

Any new module-level or shared cache must adopt one of the two patterns above:
a double-checked `Lock` with an immutable published snapshot for read-mostly
data, or a per-instance `Lock` taken around every access for mutable state. Do
not add an unguarded module-level mutable cache to `quill/core`.
