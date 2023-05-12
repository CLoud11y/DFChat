
<template>
  <div class="context-menu"
    :style="{ top: position.top + 'px', left: position.left + 'px' }"
    @click="hideContextMenu"
  >
    <slot></slot>
  </div>
</template>

<script>
export default {
  data() {
    return {
      position: {
        top: 0,
        left: 0

      }
    };
  },
  methods: {
    showContextMenu(event) {
      event.preventDefault();
      this.position.top = event.clientY;
      this.position.left = event.clientX;
      this.$el.style.display = "block";
    },
    hideContextMenu() {
      this.$el.style.display = "none";
    }
  }
};
</script>

<style scoped>
.context-menu {
  display: none;
  position: absolute;
  background-color: white;
  border: 1px solid #ccc;
}
</style>
