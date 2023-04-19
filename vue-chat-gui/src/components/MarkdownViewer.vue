<template>
  <div class="markdown-body" v-html="markdownContent"/>
</template>
<script>
import MarkdownIt from 'markdown-it';
import markdownItCodeCopy from 'markdown-it-code-copy';
import 'github-markdown-css/github-markdown.css';

export default {
  props: {
      markdown: {
        type: String,
        required: true,
      },
    },
  data() {
    return {
      md: null
    };
  },
  computed: {
    markdownContent() {
      return this.md.render(this.markdown);
    }
  },
  created() {
    this.md = new MarkdownIt({ html: true, linkify: true, typographer: true })
      .use(markdownItCodeCopy, {
        // Options
      });
  }
};
</script>
<style>
.markdown-it-code-copy {
  cursor: pointer;
  position: absolute;
  right: 0;
}
.markdown-it-code-copy::before {
  content: "copy";
  display: inline-block;
  padding: 0 1em;
  background-color: #f0f0f0;
  color: #999;
}
.markdown-it-code-copy:hover::before {
  background-color: #007bff;
  color: #fff;
}
.markdown-it-code-copy::after {
  content: "";
}
.markdown-body {
  padding: 5px 20px;
}
</style>