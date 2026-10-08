/* asl1.com structured data + canonical loader.
   Goes in GHL → Site settings → Tracking code / header, once:
     <script src="https://oyngstr.github.io/asl-schema/loader.js" defer></script>
   It fetches schema.json from the same place and, for the current page:
     - adds a <link rel="canonical"> if the page has none
     - adds one JSON-LD block, unless the page already carries one from this loader
   It never removes or edits anything GHL put on the page, and fails silently. */
(function () {
  try {
    var me = document.currentScript && document.currentScript.src;
    var base = me ? me.replace(/loader\.js.*$/, '') : 'https://oyngstr.github.io/asl-schema/';
    var path = location.pathname.replace(/\/+$/, '') || '/';

    fetch(base + 'schema.json', { cache: 'no-cache' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        if (!data || !data.pages) return;
        var page = data.pages[path];
        if (!page) return;

        if (page.canonical && !document.querySelector('link[rel="canonical"]')) {
          var link = document.createElement('link');
          link.rel = 'canonical';
          link.href = page.canonical;
          link.setAttribute('data-asl', 'canonical');
          document.head.appendChild(link);
        }

        if (page.jsonld && !document.querySelector('script[data-asl="jsonld"]')) {
          var s = document.createElement('script');
          s.type = 'application/ld+json';
          s.setAttribute('data-asl', 'jsonld');
          s.text = JSON.stringify(page.jsonld);
          document.head.appendChild(s);
        }
      })
      .catch(function () {});
  } catch (e) {}
})();
