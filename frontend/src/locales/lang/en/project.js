export default {
  project: {
    // List page
    projectManagement: 'Project Management',
    aiProjectManagement: 'Endpoint Management',
    newProject: 'New Project',
    newAiProject: 'New Endpoint',
    searchPlaceholder: 'Search project name',
    searchAiProjectPlaceholder: 'Search endpoint name',
    statusFilter: 'Status Filter',
    projectName: 'Project Name',
    aiProjectName: 'Endpoint Name',
    description: 'Description',
    status: 'Status',
    owner: 'Owner',
    createdAt: 'Created At',
    actions: 'Actions',

    // Status
    active: 'Active',
    paused: 'Paused',
    completed: 'Completed',
    archived: 'Archived',

    // Dialog
    editProject: 'Edit Project',
    editAiProject: 'Edit Endpoint',
    createProject: 'New Project',
    createAiProject: 'New Endpoint',
    projectNamePlaceholder: 'Enter project name',
    aiProjectNamePlaceholder: 'Enter endpoint name',
    projectDescription: 'Project Description',
    aiProjectDescription: 'Endpoint Description',
    projectDescriptionPlaceholder: 'Enter project description',
    aiProjectDescriptionPlaceholder: 'Enter endpoint description',
    selectStatus: 'Select status',
    update: 'Update',
    create: 'Create',

    // Validation
    projectNameRequired: 'Please enter project name',
    projectNameLength: 'Project name length must be between 2 and 200 characters',
    projectStatusRequired: 'Please select project status',

    // Messages
    fetchListFailed: 'Failed to fetch project list',
    updateSuccess: 'Project updated successfully',
    createSuccess: 'Project created successfully',
    updateFailed: 'Failed to update project',
    createFailed: 'Failed to create project',
    deleteConfirm: 'Are you sure to delete this project?',
    deleteSuccess: 'Project deleted successfully',
    deleteFailed: 'Failed to delete project',

    // Detail page
    projectDetail: 'Project Details',
    aiProjectDetail: 'Endpoint Details',
    projectInfo: 'Project Info',
    aiProjectInfo: 'Endpoint Info',
    noDescription: 'No description',
    projectMembers: 'Project Members',
    aiProjectMembers: 'Endpoint Members',
    addMember: 'Add Member',
    username: 'Username',
    email: 'Email',
    role: 'Role',
    joinedAt: 'Joined At',
    removeMember: 'Remove',
    environments: 'Environments',
    addEnvironment: 'Add Environment',
    environmentName: 'Environment Name',
    baseUrl: 'Base URL',
    defaultEnvironment: 'Default Environment',
    yes: 'Yes',
    no: 'No',
    fetchDetailFailed: 'Failed to fetch project details',
    memberDeleteSuccess: 'Member deleted successfully',
    memberDeleteFailed: 'Failed to delete member',

    // New translations for ProjectDetail
    memberList: 'Member List',
    environmentList: 'Environment List',
    user: 'User',
    selectUser: 'Please select user',
    selectRole: 'Please select role',
    admin: 'Admin',
    developer: 'Developer',
    tester: 'Tester',
    viewer: 'Viewer',
    fetchUsersFailed: 'Failed to fetch user list',
    memberAddSuccess: 'Member added successfully',
    memberAddFailed: 'Failed to add member',
    confirmRemoveMember: 'Are you sure to remove member {name}?',
    editEnvironment: 'Edit Environment',
    environmentNamePlaceholder: 'Enter environment name',
    baseUrlPlaceholder: 'Enter base URL',
    descriptionPlaceholder: 'Enter environment description',
    environmentNameRequired: 'Please enter environment name',
    baseUrlRequired: 'Please enter base URL',
    environmentAddSuccess: 'Environment added successfully',
    environmentAddFailed: 'Failed to add environment',
    environmentUpdateSuccess: 'Environment updated successfully',
    environmentUpdateFailed: 'Failed to update environment',
    environmentDeleteSuccess: 'Environment deleted successfully',
    environmentDeleteFailed: 'Failed to delete environment',
    confirmDeleteEnvironment: 'Are you sure to delete environment {name}?',
    serialNumber: 'No.',

    // Endpoint Menu Management
    menuList: 'Menu List',
    addMenu: 'Add Menu',
    addSubMenu: 'Add Sub Menu',
    editMenu: 'Edit Menu',
    menuName: 'Menu Name',
    menuDescription: 'Menu Description',
    parentMenu: 'Parent Menu',
    rootMenu: 'Root Menu',
    selectParentMenu: 'Please select parent menu',
    menuNamePlaceholder: 'Enter menu name',
    menuDescriptionPlaceholder: 'Enter menu description',
    menuNameRequired: 'Please enter menu name',
    menuNameLength: 'Menu name length must be between 1 and 100 characters',
    noMenu: 'No menus yet',
    selectMenuTip: 'Please select a menu to view details',
    addRootMenu: 'Add Root Menu',
    subMenuList: 'Sub Menu List',
    sortOrder: 'Sort Order',
    fetchMenuFailed: 'Failed to fetch menu list',
    menuCreateSuccess: 'Menu created successfully',
    menuCreateFailed: 'Failed to create menu',
    menuUpdateSuccess: 'Menu updated successfully',
    menuUpdateFailed: 'Failed to update menu',
    menuDeleteSuccess: 'Menu deleted successfully',
    menuDeleteFailed: 'Failed to delete menu',
    confirmDeleteMenu: 'Are you sure to delete menu {name}? All its sub-menus will also be deleted.'
  },
  home: {
    // Header
    user: 'User',
    logout: 'Logout',
    logoutConfirm: 'Are you sure to logout?',
    logoutSuccess: 'Logged out successfully',

    // Language
    language: {
      current: 'English',
      zhCN: '简体中文',
      en: 'English'
    },

    // Title
    title: 'TestHub Testing Platform',
    subtitle: 'All-in-One Intelligent Testing Solution',

    // Cards
    aiCaseGeneration: 'AI Intelligent Case',
    aiCaseGenerationDesc: 'Intelligently analyze requirements, auto-generate test cases',
    apiTesting: 'API Testing',
    apiTestingDesc: 'Efficient API automation testing and management',
    uiAutomation: 'UI Automation Testing',
    uiAutomationDesc: 'Visual Web/App UI automation testing',
    dataFactory: 'Data Toolkit',
    dataFactoryDesc: 'Flexible test data construction and management',
    aiIntelligentMode: 'AI Intelligent Testing',
    aiIntelligentModeDesc: 'Natural language-based intelligent test execution',
    aiEvaluator: 'AI Evaluator',
    aiEvaluatorDesc: 'Professional software testing Q&A based on evaluator knowledge base',
    configCenter: 'Configuration Center',
    configCenterDesc: 'System environment, AI model and notification configuration',

    // Messages
    featureInDevelopment: 'Feature is under development......'
  },
  profile: {
    // Page
    title: 'Profile Settings',
    basicInfo: 'Basic Information',
    changePassword: 'Change Password',

    // Basic Info
    username: 'Username',
    email: 'Email',
    name: 'Name',
    department: 'Department',
    position: 'Position',

    // Password
    currentPassword: 'Current Password',
    newPassword: 'New Password',
    confirmPassword: 'Confirm Password',
    changePasswordButton: 'Change Password'
  }
}
