// Initialize Mermaid
document$.subscribe(function() {
  mermaid.initialize({
    startOnLoad: true,
    theme: 'default'
  });

  // Re-render mermaid diagrams when navigating
  mermaid.contentLoaded();
});
