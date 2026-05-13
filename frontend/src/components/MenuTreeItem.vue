<template>
  <template v-if="menu.children && menu.children.length > 0">
    <!-- 有子菜单的节点：点击标题跳转到该菜单的用例 -->
    <el-sub-menu :index="`menu-${menu.id}`">
      <template #title>
        <div class="menu-item-wrapper" :style="{ paddingLeft: level * 12 + 'px' }" @click.stop="goToMenu(menu.id)">
          <el-icon class="menu-icon"><FolderOpened /></el-icon>
          <span class="menu-name">{{ menu.name }}</span>
        </div>
      </template>
      <!-- 递归渲染子菜单 -->
      <MenuTreeItem 
        v-for="child in menu.children" 
        :key="child.id" 
        :menu="child"
        :level="level + 1"
      />
    </el-sub-menu>
  </template>
  <template v-else>
    <!-- 叶子节点：直接点击跳转 -->
    <el-menu-item :index="`/ai-generation/testcases?menu=${menu.id}`">
      <span class="menu-title" :style="{ paddingLeft: level * 12 + 'px' }">
        <el-icon class="menu-icon"><Document /></el-icon>
        <span>{{ menu.name }}</span>
      </span>
    </el-menu-item>
  </template>
</template>

<script setup>
import { FolderOpened, Document } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'

const router = useRouter()

defineProps({
  menu: {
    type: Object,
    required: true
  },
  level: {
    type: Number,
    default: 0
  }
})

// 点击查看该菜单及其下级的用例
const goToMenu = (menuId) => {
  router.push(`/ai-generation/testcases?menu=${menuId}`)
}
</script>

<style scoped>
.menu-title,
.menu-item-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.menu-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 4px;
  font-size: 16px;
}

.menu-item-wrapper:hover .menu-icon {
  color: #7b42f6;
}
</style>
