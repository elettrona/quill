"""Edit-over-SSH support: site manager, newline-safe transfer, SFTP service.

The pieces are split so the pure logic is testable without a network or the
optional ``paramiko`` dependency:

* :mod:`quill.core.ssh.transfer` -- newline translation and backup naming
  (pure functions).
* :mod:`quill.core.ssh.sites` -- the site manager (persisted connection
  profiles; no plaintext passwords).
* :mod:`quill.core.ssh.client` -- the SFTP file service. The service takes an
  injected SFTP handle so it can be exercised with a fake; :func:`connect`
  builds a real one via ``paramiko`` and reports a plain install hint when the
  dependency is missing.
"""
