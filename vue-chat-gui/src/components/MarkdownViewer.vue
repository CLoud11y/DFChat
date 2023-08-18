<template>
    <Transition name=“blink” v-show="show&&!markdownContent" > <span>|</span> </Transition>
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
      md: null,
      show : false,
      timer:null
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
  },
  mounted(){
   const timer = setInterval(() => { this.show = !this.show; }, 500);
  },


};
</script>
<style>
.blink-enter-active, .blink-leave-active { animation: blink 0.5s; }

@keyframes blink { from { opacity: 1; } to { opacity: 0; } }
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

}
.markdown-it-code-copy:hover::before {
  background-color: #007bff;
  color: #fff;
}
.markdown-it-code-copy::after {
  content: "";
}
.markdown-body{
  padding: 0;
}
 .user .markdown-body  {
  background-color: inherit;
}  .markdown-body  {
  background-color: inherit;
} 
</style>