import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs';

export function getVersion() {
  // Read and parse pyproject.toml
  const __filename = fileURLToPath(import.meta.url);
  const __dirname = path.dirname(__filename);
  const pyprojectToml = fs.readFileSync(
    path.join(__dirname, '..', '..', '..', 'pyproject.toml'),
    'utf8'
  );

  // Extract version from pyproject.toml using regex
  const version = pyprojectToml.match(/version = "([^"]+)"/)?.[1];
  if (!version) {
    throw new Error('Could not find version in pyproject.toml');
  }
  console.log('Found Version:', version);
  return version;
}
