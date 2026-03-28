export default {
  project: {
    // List page
    projectManagement: '项目管理',
    aiProjectManagement: '端管理',
    newProject: '新建项目',
    newAiProject: '新建端',
    searchPlaceholder: '搜索项目名称',
    searchAiProjectPlaceholder: '搜索端名称',
    statusFilter: '状态筛选',
    projectName: '项目名称',
    aiProjectName: '端名称',
    description: '描述',
    status: '状态',
    owner: '负责人',
    createdAt: '创建时间',
    actions: '操作',

    // Status
    active: '进行中',
    paused: '已暂停',
    completed: '已完成',
    archived: '已归档',

    // Dialog
    editProject: '编辑项目',
    editAiProject: '编辑端',
    createProject: '新建项目',
    createAiProject: '新建端',
    projectNamePlaceholder: '请输入项目名称',
    aiProjectNamePlaceholder: '请输入端名称',
    projectDescription: '项目描述',
    aiProjectDescription: '端描述',
    projectDescriptionPlaceholder: '请输入项目描述',
    aiProjectDescriptionPlaceholder: '请输入端描述',
    selectStatus: '请选择状态',
    update: '更新',
    create: '创建',

    // Validation
    projectNameRequired: '请输入项目名称',
    projectNameLength: '项目名称长度在 2 到 200 个字符',
    projectStatusRequired: '请选择项目状态',

    // Messages
    fetchListFailed: '获取项目列表失败',
    updateSuccess: '项目更新成功',
    createSuccess: '项目创建成功',
    updateFailed: '项目更新失败',
    createFailed: '项目创建失败',
    deleteConfirm: '确定要删除这个项目吗？',
    deleteSuccess: '项目删除成功',
    deleteFailed: '项目删除失败',

    // Detail page
    projectDetail: '项目详情',
    aiProjectDetail: '端详情',
    projectInfo: '项目信息',
    aiProjectInfo: '端信息',
    noDescription: '暂无描述',
    projectMembers: '项目成员',
    aiProjectMembers: '端成员',
    addMember: '添加成员',
    username: '用户名',
    email: '邮箱',
    role: '角色',
    joinedAt: '加入时间',
    removeMember: '删除',
    environments: '环境配置',
    addEnvironment: '添加环境',
    environmentName: '环境名称',
    baseUrl: '基础URL',
    defaultEnvironment: '默认环境',
    yes: '是',
    no: '否',
    fetchDetailFailed: '获取项目详情失败',
    memberDeleteSuccess: '成员删除成功',
    memberDeleteFailed: '删除成员失败',

    // New translations for ProjectDetail
    memberList: '成员列表',
    environmentList: '环境列表',
    user: '用户',
    selectUser: '请选择用户',
    selectRole: '请选择角色',
    admin: '管理员',
    developer: '开发者',
    tester: '测试者',
    viewer: '观察者',
    fetchUsersFailed: '获取用户列表失败',
    memberAddSuccess: '成员添加成功',
    memberAddFailed: '添加成员失败',
    confirmRemoveMember: '确定要删除成员 {name} 吗？',
    editEnvironment: '编辑环境',
    environmentNamePlaceholder: '请输入环境名称',
    baseUrlPlaceholder: '请输入基础URL',
    descriptionPlaceholder: '请输入环境描述',
    environmentNameRequired: '请输入环境名称',
    baseUrlRequired: '请输入基础URL',
    environmentAddSuccess: '环境添加成功',
    environmentAddFailed: '添加环境失败',
    environmentUpdateSuccess: '环境更新成功',
    environmentUpdateFailed: '环境更新失败',
    environmentDeleteSuccess: '环境删除成功',
    environmentDeleteFailed: '删除环境失败',
    confirmDeleteEnvironment: '确定要删除环境 {name} 吗？',
    serialNumber: '序号',

    // 端菜单管理
    menuList: '菜单列表',
    addMenu: '新增菜单',
    addSubMenu: '新增子菜单',
    editMenu: '编辑菜单',
    menuName: '菜单名称',
    menuDescription: '菜单描述',
    parentMenu: '父菜单',
    rootMenu: '根菜单',
    selectParentMenu: '请选择父菜单',
    menuNamePlaceholder: '请输入菜单名称',
    menuDescriptionPlaceholder: '请输入菜单描述',
    menuNameRequired: '请输入菜单名称',
    menuNameLength: '菜单名称长度在 1 到 100 个字符',
    noMenu: '暂无菜单',
    selectMenuTip: '请选择一个菜单查看详情',
    addRootMenu: '新增根菜单',
    subMenuList: '子菜单列表',
    sortOrder: '排序',
    fetchMenuFailed: '获取菜单列表失败',
    menuCreateSuccess: '菜单创建成功',
    menuCreateFailed: '菜单创建失败',
    menuUpdateSuccess: '菜单更新成功',
    menuUpdateFailed: '菜单更新失败',
    menuDeleteSuccess: '菜单删除成功',
    menuDeleteFailed: '菜单删除失败',
    confirmDeleteMenu: '确定要删除菜单 {name} 吗？删除后其所有子菜单也会被删除。'
  },
  home: {
    // Header
    user: '用户',
    logout: '退出登录',
    logoutConfirm: '确定要退出登录吗？',
    logoutSuccess: '已退出登录',

    // Language
    language: {
      current: '中文',
      zhCN: '简体中文',
      en: 'English'
    },

    // Title
    title: 'TestMatrix 进阶 TestHub',
    subtitle: '',

    // Cards
    aiCase: 'AI智能用例',
    aiCaseDesc: '智能分析需求，自动生成测试用例',
    apiTesting: '接口测试',
    apiTestingDesc: '高效的接口自动化测试与管理',
    uiAutomation: 'UI自动化测试',
    uiAutomationDesc: '可视化的Web/App UI自动化测试',
    dataFactory: '数据工具箱',
    dataFactoryDesc: '灵活的测试数据构造与管理',
    aiIntelligent: 'AI智能测试',
    aiIntelligentDesc: '基于自然语言的智能化测试执行',
    aiKnowledgeBase: 'AI知识库',
    aiKnowledgeBaseDesc: '支持三方/自建知识库，提供专业问答',
    configCenter: '配置中心',
    configCenterDesc: '系统环境、AI模型及通知配置',

    // Messages
    featureInDevelopment: '功能正在开发中......'
  },
  profile: {
    // Page
    title: '个人设置',
    basicInfo: '基本信息',
    changePassword: '修改密码',

    // Basic Info
    username: '用户名',
    email: '邮箱',
    name: '姓名',
    department: '部门',
    position: '职位',

    // Password
    currentPassword: '当前密码',
    newPassword: '新密码',
    confirmPassword: '确认密码',
    changePasswordButton: '修改密码'
  }
}
