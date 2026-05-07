# CSS 修复经验记录

## 问题：Element Plus el-select 下拉框显示紫色/黄色背景

### 现象
Element Plus 的 el-select 组件在 Chrome 浏览器中显示为浅紫色或淡黄色背景，这是由于浏览器自动填充（autofill）功能导致的。

### 根本原因
1. **浏览器自动填充**：Chrome 等浏览器会对表单元素自动填充历史数据，默认使用淡黄色/紫色背景
2. **Element Plus 2.x 组件结构**：el-select 使用 `.el-select__wrapper` 作为包装器，而不是 `.el-input__wrapper`
3. **CSS 变量优先级**：Element Plus 使用 CSS 变量（--el-input-bg-color 等）控制背景色

### 解决方案

#### 方法一：全局样式覆盖（推荐）
在 `src/assets/css/global.scss` 中添加：

```scss
// 全局覆盖 Element Plus 输入框和下拉框背景色
// 使用 html body 前缀提高优先级
html body .el-input__wrapper {
  background-color: #ffffff !important;
  background: #ffffff !important;
}

html body .el-input__inner {
  background-color: #ffffff !important;
  background: #ffffff !important;
}

html body .el-select .el-input__wrapper {
  background-color: #ffffff !important;
  background: #ffffff !important;
}

html body .el-select .el-input__inner {
  background-color: #ffffff !important;
  background: #ffffff !important;
}

// Element Plus 2.x 使用 .el-select__wrapper
html body .el-select .el-select__wrapper {
  background-color: #ffffff !important;
  background: #ffffff !important;
}

// 覆盖 Element Plus CSS 变量
html body {
  --el-input-bg-color: #ffffff !important;
  --el-fill-color-blank: #ffffff !important;
  --el-select-bg-color: #ffffff !important;
}

// 覆盖浏览器自动填充的黄色/紫色背景
input:-webkit-autofill,
input:-webkit-autofill:hover,
input:-webkit-autofill:focus,
input:-webkit-autofill:active {
  -webkit-box-shadow: 0 0 0 1000px #ffffff inset !important;
  box-shadow: 0 0 0 1000px #ffffff inset !important;
  -webkit-text-fill-color: #1f2937 !important;
  background-color: #ffffff !important;
  background: #ffffff !important;
  transition: background-color 5000s ease-in-out 0s !important;
}
```

#### 方法二：组件级样式（针对特定对话框）
在组件文件中添加非 scoped 样式：

```vue
<style lang="scss">
// 全局样式 - 使用 html body 前缀提高优先级
html body .your-dialog-class {
  --el-input-bg-color: #ffffff !important;
  --el-fill-color-blank: #ffffff !important;
  
  .el-select {
    // Element Plus 2.x 的主要选择器
    .el-select__wrapper {
      background-color: #ffffff !important;
      background: #ffffff !important;
    }
    
    // 备用选择器
    .el-input__wrapper {
      background-color: #ffffff !important;
      background: #ffffff !important;
    }
    
    .el-input__inner {
      background-color: #ffffff !important;
      background: #ffffff !important;
    }
  }
}

// 额外全局覆盖
html body .el-select .el-select__wrapper {
  background-color: #ffffff !important;
}
</style>
```

### 关键要点

1. **Element Plus 2.x 类名变化**：
   - el-select 使用 `.el-select__wrapper` 作为主要包装器
   - 同时保留 `.el-input__wrapper` 作为兼容性选择器

2. **提高 CSS 优先级**：
   - 使用 `html body` 前缀提高选择器优先级
   - 使用 `!important` 覆盖内联样式

3. **覆盖浏览器自动填充**：
   - 使用 `-webkit-box-shadow: 0 0 0 1000px #ffffff inset` 覆盖自动填充背景
   - 使用 `transition: background-color 5000s` 延迟背景色变化

4. **CSS 变量覆盖**：
   - `--el-input-bg-color`: 输入框背景色
   - `--el-fill-color-blank`: 空白填充色
   - `--el-select-bg-color`: 选择框背景色

### 调试技巧

1. 使用 Chrome DevTools 检查实际应用的样式
2. 检查 Elements 面板中的类名（`.el-select__wrapper` vs `.el-input__wrapper`）
3. 查看 Computed 面板中的 background-color 来源
4. 强制刷新清除缓存：Ctrl+F5 或 Cmd+Shift+R

### 参考文件

- `src/assets/css/global.scss` - 全局样式文件
- `src/views/api-testing/components/ImportDialog.vue` - 修复示例组件

### 记录时间
2026-05-06

### 相关技术
- Vue 3
- Element Plus 2.x
- Chrome 自动填充
- CSS 优先级
