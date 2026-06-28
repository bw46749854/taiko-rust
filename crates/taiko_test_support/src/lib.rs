//! Test-support helpers shared by the loop CLI and future harness tickets.

use std::fs;
use std::io;
use std::path::{Path, PathBuf};

/// Repository-relative path used by Loop CLI commands.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct RepoPath {
    inner: PathBuf,
}

impl RepoPath {
    /// Creates a repository path wrapper.
    #[must_use]
    pub fn new(path: impl Into<PathBuf>) -> Self {
        Self { inner: path.into() }
    }

    /// Returns the wrapped path.
    #[must_use]
    pub fn as_path(&self) -> &Path {
        &self.inner
    }

    /// Returns whether the wrapped path exists.
    #[must_use]
    pub fn exists(&self) -> bool {
        self.inner.exists()
    }
}

/// Reads a UTF-8 text file. The helper keeps error reporting explicit for CLI use.
pub fn read_utf8(path: &Path) -> io::Result<String> {
    fs::read_to_string(path)
}

/// Lists Markdown files in a directory, sorted lexicographically.
pub fn list_markdown_files(path: &Path) -> io::Result<Vec<PathBuf>> {
    let mut files = Vec::new();
    for entry in fs::read_dir(path)? {
        let entry = entry?;
        let candidate = entry.path();
        if candidate.extension().and_then(|ext| ext.to_str()) == Some("md") {
            files.push(candidate);
        }
    }
    files.sort();
    Ok(files)
}

#[cfg(test)]
mod tests {
    use super::RepoPath;

    #[test]
    fn repo_path_preserves_path() {
        let path = RepoPath::new("AGENTS.md");
        assert_eq!(path.as_path().to_string_lossy(), "AGENTS.md");
    }
}
