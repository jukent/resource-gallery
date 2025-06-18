import { spawn } from 'node:child_process';


/**
 * Call out to an external process that conforms to a JSON-based 
 * stdin-stdout transform specification.
 *
 * @param opts transform options, containing the binary path and arguments
 */
function externalTransform(opts) {
  return async (mdast) => {
    const data = JSON.stringify(mdast);
    const subprocess = spawn(opts.executable, opts.args ?? []);

    // Pass in the data
    subprocess.stdin.write(data);
    subprocess.stdin.end();

    // Read out the response in chunks
    const buffers = [];
    subprocess.stdout.on('data', (chunk) => {
      buffers.push(chunk);
    });

    // Await exit
    await new Promise((resolve) => {
      subprocess.on('close', resolve);
    });
    // Concatenate the responses
    const stdout = Buffer.concat(buffers).toString();

    // Modify the tree in-place
    const result = JSON.parse(stdout);
    Object.assign(mdast, result);
  };
}

const resourcesTransform = () =>
  externalTransform({ executable: 'python3', args: ['pythia-gallery.py'] });

const pythiaGalleryDirective = {
  name: 'pythia-resources',
  doc: 'An example directive for embedding a Pythia resource gallery.',
  run() {
    const img = { type: 'pythia-resources', children: [] };
    return [img];
  },
};
const pythiaGalleryTransform = {
  plugin: resourcesTransform,
  stage: 'document',
};

const plugin = {
  name: 'Pythia Gallery',
  directives: [pythiaGalleryDirective],
  transforms: [pythiaGalleryTransform],
};

export default plugin;