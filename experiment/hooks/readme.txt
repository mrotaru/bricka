The idea is to experiment and define a hook mechanism.

Each tool can define one or multiple hooks, to be called by waf.

Each tool must have a 'hook' attribute, which is of the form ['<type>','<parameters>']

There are three types of hooks:
- extension - file extensions (ex: html, css, etc)
- tag - these are valid for html/xml files, and can be attached to any tag (ex:
  script, img, etc)

  The callback function will be passed the fragment, including the tags - this would
  allow the processing of the attributes. Such tasks are expected to process the
  fragment, and place the output in an `output` member variable.

- comment - instructions for the build system placed in comments. At the
  moment, only valid inside HTML, but it would be theoretically possible to
  apply the same concept to other file types.

  Much like tag hooks, the callback function of a tool which uses a comment hook will
  be passed the contents between the opening and closing comments. They are also
  expected to fill the `output` attribute with the result.

  Also like tag hooks, they must support nesting. If a comment hook contains other
  hooks (comment or tag), they will be processed first, and the outermost hook will
  operate on the output of the inner hook callbacks results.
