'use strict';

// @tufjs/models@3.0.1 exposes Signed.expires as an ISO string, while later
// versions expose a Date-like value. The frozen representation builder calls
// toISOString() only to serialize this descriptive field. This shim normalizes
// the v3.0.1 string API without changing any representation mapping, signature
// verification, qualification rule, or scoring logic.
if (typeof String.prototype.toISOString !== 'function') {
  Object.defineProperty(String.prototype, 'toISOString', {
    value: function () { return String(this); },
    configurable: true,
    enumerable: false,
    writable: true,
  });
}
