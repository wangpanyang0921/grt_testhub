<template>
  <div class="key-value-editor">
    <div v-if="showSectionTitle" class="section-title">Headers</div>
    <div class="editor-container">
      <div class="header">
        <div class="column checkbox-column"></div>
        <div class="column key-column">参数名</div>
        <div class="column value-column">参数值</div>
        <div class="column type-column">类型</div>
        <div class="column description-column">描述</div>
        <div class="column action-column"></div>
      </div>

    <div class="rows">
      <div
        v-for="(row, index) in rows"
        :key="index"
        class="row"
        :class="{ disabled: !row.enabled }"
      >
        <div class="column checkbox-column">
          <el-checkbox v-model="row.enabled" @change="updateValue" />
        </div>
        <div class="column key-column">
          <el-input
            v-model="row.key"
            :placeholder="placeholderKey"
            size="small"
            @input="updateValue"
          />
        </div>

        <div class="column value-column">
          <el-input
            v-if="!showFile || row.type !== 'file'"
            v-model="row.value"
            :placeholder="placeholderValue"
            size="small"
            @input="updateValue"
          >
            <template #append>
              <el-button
                size="small"
                @click="openDataFactorySelector(index)"
                title="引用数据工厂"
              >
                <el-icon><MagicStick /></el-icon>
              </el-button>
            </template>
          </el-input>
          <el-upload
            v-else
            :auto-upload="false"
            :show-file-list="false"
            @change="(file) => handleFileChange(index, file)"
          >
            <el-button size="small">{{ $t('apiTesting.component.keyValueEditor.selectFile') }}</el-button>
          </el-upload>
          <el-tooltip :content="$t('apiTesting.component.keyValueEditor.insertDynamicVariable')" placement="top" v-if="!showFile || row.type !== 'file'">
            <el-button
              size="small"
              class="variable-helper-btn"
              @click="openVariableHelper(index)"
            >
              <el-icon><MagicStick /></el-icon>
            </el-button>
          </el-tooltip>
          <span v-if="row.file" class="file-name">{{ row.file.name }}</span>
        </div>

        <div class="column type-column">
          <el-select
            v-model="row.type"
            placeholder="类型"
            size="small"
            style="width: 90px;"
            @change="updateValue"
          >
            <el-option label="string" value="string" />
            <el-option label="integer" value="integer" />
            <el-option label="boolean" value="boolean" />
            <el-option label="number" value="number" />
            <el-option label="array" value="array" />
            <el-option label="file" value="file" />
          </el-select>
        </div>

        <div class="column description-column">
          <el-input
            v-model="row.description"
            :placeholder="$t('apiTesting.component.keyValueEditor.description')"
            size="small"
            @input="updateValue"
          />
        </div>

        <div class="column action-column">
          <el-button
            size="small"
            @click="addRow"
            :title="$t('apiTesting.component.keyValueEditor.addRow')"
          >
            <el-icon><Plus /></el-icon>
          </el-button>

          <el-button
            size="small"
            type="danger"
            :icon="Delete"
            @click="removeRow(index)"
            :disabled="rows.length <= 1"
          />
        </div>
      </div>
    </div>
    </div>

    <!-- 全局 Header 参数区域 -->
    <div v-if="globalHeaders && globalHeaders.length > 0" class="global-headers-section">
      <div class="global-headers-title">全局 Headers</div>
      <div class="global-headers-editor">
        <div class="global-headers-header">
          <div class="column checkbox-column"></div>
          <div class="column key-column">参数名</div>
          <div class="column value-column">参数值</div>
          <div class="column type-column">类型</div>
          <div class="column description-column">描述</div>
          <div class="column action-column"></div>
        </div>
        <div class="global-headers-list">
          <div
            v-for="(row, index) in globalHeaders"
            :key="'global-'+index"
            class="row global-row"
            :class="{ disabled: !row.enabled }"
          >
            <div class="column checkbox-column">
              <el-checkbox v-model="row.enabled" @change="updateGlobalHeader(index, row)" />
            </div>
            <div class="column key-column">
              <el-input
                v-model="row.key"
                placeholder="参数名"
                size="small"
                disabled
              />
            </div>

            <div class="column value-column">
              <el-input
                v-model="row.value"
                placeholder="参数值"
                size="small"
                disabled
              />
            </div>

            <div class="column type-column">
              <el-select
                v-model="row.type"
                placeholder="类型"
                size="small"
                style="width: 90px;"
                disabled
              >
                <el-option label="string" value="string" />
                <el-option label="integer" value="integer" />
                <el-option label="boolean" value="boolean" />
                <el-option label="number" value="number" />
                <el-option label="array" value="array" />
                <el-option label="file" value="file" />
              </el-select>
            </div>

            <div class="column description-column">
              <el-input
                v-model="row.description"
                placeholder="描述"
                size="small"
                disabled
              />
            </div>

            <div class="column action-column">
              <!-- 操作列留白 -->
            </div>
          </div>
        </div>
      </div>
    </div>

    <DataFactorySelector
      v-model="showDataFactorySelector"
      @select="handleDataFactorySelect"
    />

    <el-dialog
      :close-on-press-escape="false"
      :modal="true"
      :destroy-on-close="false"
      v-model="showVariableHelper"
      :title="$t('apiTesting.component.keyValueEditor.variableHelper')"
      :close-on-click-modal="false"
      width="1100px"
      class="variable-helper-dialog"
    >
      <el-tabs style="height: 500px" class="variable-tabs">
        <el-tab-pane
          v-for="(category, index) in variableCategories"
          :key="index"
          :label="category.label"
        >
          <div style="height: 460px; overflow-y: auto; padding: 10px;">
            <el-table :data="category.variables" style="width: 100%" @row-click="insertVariable" highlight-current-row>
              <el-table-column prop="name" :label="$t('apiTesting.component.keyValueEditor.functionName')" min-width="180" show-overflow-tooltip>
                <template #default="{ row }">
                  <el-tag size="small">{{ row.name }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="desc" :label="$t('apiTesting.component.keyValueEditor.desc')" min-width="100" show-overflow-tooltip />
              <el-table-column prop="syntax" :label="$t('apiTesting.component.keyValueEditor.syntax')" min-width="280" show-overflow-tooltip />
              <el-table-column prop="example" :label="$t('apiTesting.component.keyValueEditor.example')" min-width="200" show-overflow-tooltip />
              <el-table-column :label="$t('apiTesting.component.keyValueEditor.operation')" width="60">
                <template #default="{ row }">
                  <el-button link type="primary" size="small">{{ $t('apiTesting.component.keyValueEditor.insert') }}</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus, Delete, MagicStick } from '@element-plus/icons-vue'
import DataFactorySelector from '@/components/DataFactorySelector.vue'
import { ElMessage } from 'element-plus'

const { t } = useI18n()

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  },
  placeholderKey: {
    type: String,
    default: 'Key'
  },
  placeholderValue: {
    type: String,
    default: 'Value'
  },
  showFile: {
    type: Boolean,
    default: false
  },
  globalHeaders: {
    type: Array,
    default: () => []
  },
  showSectionTitle: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue', 'update:globalHeaders'])

const rows = ref([])
const showDataFactorySelector = ref(false)
const showVariableHelper = ref(false)
const currentRowIndex = ref(0)

const variableCategories = computed(() => [
  {
    label: t('apiTesting.component.keyValueEditor.categories.randomNumber'),
    variables: [
      { name: 'random_int', syntax: '${random_int(min, max, count)}', desc: t('apiTesting.component.keyValueEditor.variables.randomInt'), example: '${random_int(100, 999, 1)}' },
      { name: 'random_float', syntax: '${random_float(min, max, precision, count)}', desc: t('apiTesting.component.keyValueEditor.variables.randomFloat'), example: '${random_float(0, 1, 2, 1)}' },
      { name: 'random_boolean', syntax: '${random_boolean(count)}', desc: t('apiTesting.component.keyValueEditor.variables.randomBoolean'), example: '${random_boolean(1)}' },
      { name: 'random_date', syntax: '${random_date(start_date, end_date, count, date_format)}', desc: t('apiTesting.component.keyValueEditor.variables.randomDate'), example: '${random_date(2024-01-01, 2024-12-31, 1, %Y-%m-%d)}' }
    ]
  },
  {
    label: t('apiTesting.component.keyValueEditor.categories.randomString'),
    variables: [
      { name: 'random_string', syntax: '${random_string(length, char_type, count)}', desc: t('apiTesting.component.keyValueEditor.variables.randomString'), example: '${random_string(8, all, 1)}' },
      { name: 'random_uuid', syntax: '${random_uuid(version, count)}', desc: t('apiTesting.component.keyValueEditor.variables.randomUuid'), example: '${random_uuid(4, 1)}' },
      { name: 'random_mac_address', syntax: '${random_mac_address(separator, count)}', desc: t('apiTesting.component.keyValueEditor.variables.randomMacAddress'), example: '${random_mac_address(:, 1)}' },
      { name: 'random_ip_address', syntax: '${random_ip_address(ip_version, count)}', desc: t('apiTesting.component.keyValueEditor.variables.randomIpAddress'), example: '${random_ip_address(4, 1)}' },
      { name: 'random_sequence', syntax: '${random_sequence(sequence, count, unique)}', desc: t('apiTesting.component.keyValueEditor.variables.randomSequence'), example: '${random_sequence([a,b,c], 1, false)}' }
    ]
  },
  {
    label: t('apiTesting.component.keyValueEditor.categories.stringUtils'),
    variables: [
      { name: 'remove_whitespace', syntax: '${remove_whitespace(text, type)}', desc: t('apiTesting.component.keyValueEditor.variables.removeWhitespace'), example: '${remove_whitespace(hello world, all)}' },
      { name: 'replace_string', syntax: '${replace_string(text, old, new, count)}', desc: t('apiTesting.component.keyValueEditor.variables.replaceString'), example: '${replace_string(hello world, world, test, 1)}' },
      { name: 'word_count', syntax: '${word_count(text)}', desc: t('apiTesting.component.keyValueEditor.variables.wordCount'), example: '${word_count(hello world)}' },
      { name: 'regex_test', syntax: '${regex_test(text, pattern, flags)}', desc: t('apiTesting.component.keyValueEditor.variables.regexTest'), example: '${regex_test(hello123, ^[a-z]+\\d+$, gi)}' },
      { name: 'case_convert', syntax: '${case_convert(text, case_type)}', desc: t('apiTesting.component.keyValueEditor.variables.caseConvert'), example: '${case_convert(hello, upper)}' }
    ]
  },
  {
    label: t('apiTesting.component.keyValueEditor.categories.testData'),
    variables: [
      { name: 'generate_chinese_name', syntax: '${generate_chinese_name(gender, count)}', desc: t('apiTesting.component.keyValueEditor.variables.generateChineseName'), example: '${generate_chinese_name(random, 1)}' },
      { name: 'generate_chinese_phone', syntax: '${generate_chinese_phone(count)}', desc: t('apiTesting.component.keyValueEditor.variables.generateChinesePhone'), example: '${generate_chinese_phone(1)}' },
      { name: 'generate_chinese_email', syntax: '${generate_chinese_email(count)}', desc: t('apiTesting.component.keyValueEditor.variables.generateChineseEmail'), example: '${generate_chinese_email(1)}' },
      { name: 'generate_chinese_address', syntax: '${generate_chinese_address(full_address, count)}', desc: t('apiTesting.component.keyValueEditor.variables.generateChineseAddress'), example: '${generate_chinese_address(true, 1)}' },
      { name: 'generate_id_card', syntax: '${generate_id_card(count)}', desc: t('apiTesting.component.keyValueEditor.variables.generateIdCard'), example: '${generate_id_card(1)}' },
      { name: 'generate_company_name', syntax: '${generate_company_name(count)}', desc: t('apiTesting.component.keyValueEditor.variables.generateCompanyName'), example: '${generate_company_name(1)}' },
      { name: 'generate_bank_card', syntax: '${generate_bank_card(count)}', desc: t('apiTesting.component.keyValueEditor.variables.generateBankCard'), example: '${generate_bank_card(1)}' },
      { name: 'generate_hk_id_card', syntax: '${generate_hk_id_card(count)}', desc: t('apiTesting.component.keyValueEditor.variables.generateHkIdCard'), example: '${generate_hk_id_card(1)}' },
      { name: 'generate_business_license', syntax: '${generate_business_license(count)}', desc: t('apiTesting.component.keyValueEditor.variables.generateBusinessLicense'), example: '${generate_business_license(1)}' },
      { name: 'generate_user_profile', syntax: '${generate_user_profile(count)}', desc: t('apiTesting.component.keyValueEditor.variables.generateUserProfile'), example: '${generate_user_profile(1)}' },
      { name: 'generate_coordinates', syntax: '${generate_coordinates(count)}', desc: t('apiTesting.component.keyValueEditor.variables.generateCoordinates'), example: '${generate_coordinates(1)}' }
    ]
  },
  {
    label: t('apiTesting.component.keyValueEditor.categories.dateTime'),
    variables: [
      { name: 'timestamp_convert', syntax: '${timestamp_convert(timestamp, convert_type)}', desc: t('apiTesting.component.keyValueEditor.variables.timestampConvert'), example: '${timestamp_convert(1234567890, to_datetime)}' },
      { name: 'random_date', syntax: '${random_date(start_date, end_date, count, date_format)}', desc: t('apiTesting.component.keyValueEditor.variables.randomDate'), example: '${random_date(2024-01-01, 2024-12-31, 1, %Y-%m-%d)}' }
    ]
  },
  {
    label: t('apiTesting.component.keyValueEditor.categories.encoding'),
    variables: [
      { name: 'base64_encode', syntax: '${base64_encode(text, encoding)}', desc: t('apiTesting.component.keyValueEditor.variables.base64Encode'), example: '${base64_encode("123456", "utf-8")}' },
      { name: 'base64_decode', syntax: '${base64_decode(text, encoding)}', desc: t('apiTesting.component.keyValueEditor.variables.base64Decode'), example: '${base64_decode("MTIzNDU2", "utf-8")}' },
      { name: 'url_encode', syntax: '${url_encode(data, encoding)}', desc: t('apiTesting.component.keyValueEditor.variables.urlEncode'), example: '${url_encode("hello world", "utf-8")}' },
      { name: 'url_decode', syntax: '${url_decode(data, encoding)}', desc: t('apiTesting.component.keyValueEditor.variables.urlDecode'), example: '${url_decode("hello%20world", "utf-8")}' },
      { name: 'unicode_convert', syntax: '${unicode_convert(text, convert_type)}', desc: t('apiTesting.component.keyValueEditor.variables.unicodeConvert'), example: '${unicode_convert("你好", "to_unicode")}' },
      { name: 'ascii_convert', syntax: '${ascii_convert(text, convert_type)}', desc: t('apiTesting.component.keyValueEditor.variables.asciiConvert'), example: '${ascii_convert("ABC", "to_ascii")}' },
      { name: 'color_convert', syntax: '${color_convert(color, from_type, to_type)}', desc: t('apiTesting.component.keyValueEditor.variables.colorConvert'), example: '${color_convert("#ff0000", "hex", "rgb")}' },
      { name: 'base_convert', syntax: '${base_convert(number, from_base, to_base)}', desc: t('apiTesting.component.keyValueEditor.variables.baseConvert'), example: '${base_convert(10, 10, 16)}' },
      { name: 'timestamp_convert', syntax: '${timestamp_convert(timestamp, convert_type)}', desc: t('apiTesting.component.keyValueEditor.variables.timestampConvert'), example: '${timestamp_convert(1234567890, "to_datetime")}' },
      { name: 'generate_barcode', syntax: '${generate_barcode(data, format)}', desc: t('apiTesting.component.keyValueEditor.variables.generateBarcode'), example: '${generate_barcode("123456", "code128")}' },
      { name: 'generate_qrcode', syntax: '${generate_qrcode(data)}', desc: t('apiTesting.component.keyValueEditor.variables.generateQrcode'), example: '${generate_qrcode("https://example.com")}' },
      { name: 'decode_qrcode', syntax: '${decode_qrcode(data)}', desc: t('apiTesting.component.keyValueEditor.variables.decodeQrcode'), example: '${decode_qrcode("/path/to/image.png")}' },
      { name: 'image_to_base64', syntax: '${image_to_base64(image_path)}', desc: t('apiTesting.component.keyValueEditor.variables.imageToBase64'), example: '${image_to_base64("/path/to/image.png")}' },
      { name: 'base64_to_image', syntax: '${base64_to_image(base64_data, output_path)}', desc: t('apiTesting.component.keyValueEditor.variables.base64ToImage'), example: '${base64_to_image("data:image/png;base64,...", "/path/to/output.png")}' }
    ]
  },
  {
    label: t('apiTesting.component.keyValueEditor.categories.encryption'),
    variables: [
      { name: 'md5_hash', syntax: '${md5_hash(text)}', desc: t('apiTesting.component.keyValueEditor.variables.md5Hash'), example: '${md5_hash("123456")}' },
      { name: 'sha1_hash', syntax: '${sha1_hash(text)}', desc: t('apiTesting.component.keyValueEditor.variables.sha1Hash'), example: '${sha1_hash("123456")}' },
      { name: 'sha256_hash', syntax: '${sha256_hash(text)}', desc: t('apiTesting.component.keyValueEditor.variables.sha256Hash'), example: '${sha256_hash("123456")}' },
      { name: 'sha512_hash', syntax: '${sha512_hash(text)}', desc: t('apiTesting.component.keyValueEditor.variables.sha512Hash'), example: '${sha512_hash("123456")}' },
      { name: 'hash_comparison', syntax: '${hash_comparison(hash1, hash2)}', desc: t('apiTesting.component.keyValueEditor.variables.hashComparison'), example: '${hash_comparison("hash1", "hash2")}' },
      { name: 'aes_encrypt', syntax: '${aes_encrypt(text, password, mode)}', desc: t('apiTesting.component.keyValueEditor.variables.aesEncrypt'), example: '${aes_encrypt("hello", "password", "CBC")}' },
      { name: 'aes_decrypt', syntax: '${aes_decrypt(encrypted_text, password, mode)}', desc: t('apiTesting.component.keyValueEditor.variables.aesDecrypt'), example: '${aes_decrypt("encrypted", "password", "CBC")}' }
    ]
  },
  {
    label: t('apiTesting.component.keyValueEditor.categories.crontab'),
    variables: [
      { name: 'generate_expression', syntax: '${generate_expression(minute, hour, day, month, weekday)}', desc: t('apiTesting.component.keyValueEditor.variables.generateExpression'), example: '${generate_expression("*", "*", "*", "*", "*")}' },
      { name: 'parse_expression', syntax: '${parse_expression(expression)}', desc: t('apiTesting.component.keyValueEditor.variables.parseExpression'), example: '${parse_expression("0 0 * * *")}' },
      { name: 'get_next_runs', syntax: '${get_next_runs(expression, count)}', desc: t('apiTesting.component.keyValueEditor.variables.getNextRuns'), example: '${get_next_runs("0 0 * * *", 5)}' },
      { name: 'validate_expression', syntax: '${validate_expression(expression)}', desc: t('apiTesting.component.keyValueEditor.variables.validateExpression'), example: '${validate_expression("0 0 * * *")}' }
    ]
  },
  {
    label: t('apiTesting.component.keyValueEditor.categories.other'),
    variables: [
      { name: 'random_password', syntax: '${random_password(length, include_uppercase, include_lowercase, include_digits, include_special, count)}', desc: t('apiTesting.component.keyValueEditor.variables.randomPassword'), example: '${random_password(12, true, true, true, true, 1)}' },
      { name: 'random_color', syntax: '${random_color(format, count)}', desc: t('apiTesting.component.keyValueEditor.variables.randomColor'), example: '${random_color(hex, 1)}' },
      { name: 'jwt_decode', syntax: '${jwt_decode(token, verify, secret)}', desc: t('apiTesting.component.keyValueEditor.variables.jwtDecode'), example: '${jwt_decode(token, false, secret)}' },
      { name: 'password_strength', syntax: '${password_strength(password)}', desc: t('apiTesting.component.keyValueEditor.variables.passwordStrength'), example: '${password_strength(myPassword123)}' },
      { name: 'generate_salt', syntax: '${generate_salt(length)}', desc: t('apiTesting.component.keyValueEditor.variables.generateSalt'), example: '${generate_salt(16)}' }
    ]
  }
])

const initializeRows = () => {
  const data = props.modelValue || {}
  console.log('KeyValueEditor initializeRows called with data:', data)
  const newRows = []

  // 检查数据是否为数组格式（来自convertObjectToKeyValueArray）
  if (Array.isArray(data)) {
    console.log('Data is array, processing...')
    // 如果是数组，直接使用
    newRows.push(...data.map(item => ({
      enabled: item.enabled !== false,
      key: item.key || '',
      value: item.value || '',
      description: item.description || '',
      type: item.type || 'string',
      file: item.file || null
    })))
  } else {
    console.log('Data is object, converting...')
    // 如果是对象，转换为行数据
    Object.keys(data).forEach(key => {
      if (key && data[key] !== undefined) {
        newRows.push({
          enabled: true,
          key,
          value: data[key],
          description: '',
          type: 'string',
          file: null
        })
      }
    })
  }

  // 确保至少有一个空行
  if (newRows.length === 0) {
    newRows.push({
      enabled: true,
      key: '',
      value: '',
      description: '',
      type: 'string',
      file: null
    })
  }

  console.log('KeyValueEditor final rows:', newRows)
  rows.value = newRows
}

const updateValue = () => {
  // 发送完整的行数据数组，而不是简化的key-value对象
  const result = rows.value.filter(row => row.key || row.value || row.description).map(row => ({
    key: row.key || '',
    value: row.value || '',
    description: row.description || '',
    enabled: row.enabled !== false,
    type: row.type || 'string'
  }))
  
  console.log('KeyValueEditor updateValue result (full format):', result)
  emit('update:modelValue', result)
  
  // 如果最后一行有内容，自动添加新行
  const lastRow = rows.value[rows.value.length - 1]
  if (lastRow.key || lastRow.value) {
    addRow()
  }
}

const addRow = () => {
  rows.value.push({
    enabled: true,
    key: '',
    value: '',
    description: '',
    type: 'string',
    file: null
  })
}

const removeRow = (index) => {
  if (rows.value.length > 1) {
    rows.value.splice(index, 1)
    updateValue()
  }
}

// 更新全局 Header 启用状态
const updateGlobalHeader = (index, row) => {
  const updatedHeaders = [...props.globalHeaders]
  updatedHeaders[index] = { ...row }
  emit('update:globalHeaders', updatedHeaders)
}

const handleFileChange = (index, file) => {
  rows.value[index].file = file
  rows.value[index].value = file.name
  updateValue()
}

const openDataFactorySelector = (index) => {
  currentRowIndex.value = index
  showDataFactorySelector.value = true
}

const handleDataFactorySelect = (record) => {
  const rowIndex = currentRowIndex.value
  if (record && record.output_data) {
    let valueToSet = ''

    if (typeof record.output_data === 'string') {
      valueToSet = record.output_data
    } else if (record.output_data.result) {
      valueToSet = record.output_data.result
    } else if (record.output_data.output_data) {
      valueToSet = record.output_data.output_data
    } else {
      valueToSet = JSON.stringify(record.output_data)
    }

    rows.value[rowIndex].value = valueToSet
    rows.value[rowIndex].description = t('apiTesting.component.keyValueEditor.fromDataFactory', { name: record.tool_name })
    updateValue()
  }
  showDataFactorySelector.value = false
}

const openVariableHelper = (index) => {
  currentRowIndex.value = index
  showVariableHelper.value = true
}

const insertVariable = (variable) => {
  const rowIndex = currentRowIndex.value
  const example = variable.example

  const currentValue = rows.value[rowIndex].value || ''
  if (!currentValue) {
    rows.value[rowIndex].value = example
  } else {
    rows.value[rowIndex].value = currentValue + example
  }

  ElMessage.success(t('apiTesting.component.keyValueEditor.variableInserted', { name: variable.name }))
  showVariableHelper.value = false
  updateValue()
}

// 监听props.modelValue变化
watch(
  () => props.modelValue,
  () => {
    initializeRows()
  },
  { immediate: true }
)

// 暴露rows供父组件访问
defineExpose({
  rows
})
</script>

<style scoped>
.key-value-editor {
  background: #ffffff;
}

.section-title {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 3px solid #67c23a;
}

.editor-container {
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  margin-bottom: 20px;
}

.header {
  display: flex;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  padding: 12px 16px;
  font-weight: 600;
  font-size: 13px;
  color: #606266;

  .column {
    justify-content: flex-start;
    align-items: center;
    padding: 0 8px;
    box-sizing: border-box;

    &:first-child {
      padding-left: 0;
    }

    &:last-child {
      padding-right: 0;
    }
  }
}

.rows {
  max-height: 300px;
  overflow-y: auto;
  overflow-x: hidden;
}

.row {
  display: flex;
  border-bottom: 1px solid #f5f7fa;
  padding: 12px 16px;
  min-height: 56px;
  align-items: center;
  transition: all 0.25s ease;
}

.row:hover {
  background: #f5f7fa;
}

.row.disabled {
  opacity: 0.5;
  background: #fafafa;
}

.column {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 8px;
  box-sizing: border-box;

  &:first-child {
    padding-left: 0;
  }

  &:last-child {
    padding-right: 0;
  }
}

.checkbox-column {
  width: 40px;
  min-width: 40px;
  justify-content: center;
}

.key-column {
  width: 20%;
  min-width: 120px;
}

.value-column {
  width: 30%;
  min-width: 180px;
}

.type-column {
  width: 100px;
  min-width: 100px;
}

.description-column {
  width: 20%;
  min-width: 100px;
}

.action-column {
  width: 90px;
  min-width: 90px;
  justify-content: flex-end;
  gap: 6px;
}

.variable-helper-btn {
  background: linear-gradient(135deg, #67c23a 0%, #5daf34 100%);
  border: none;
  color: white;
  border-radius: 6px;
  transition: all 0.3s ease;
}

.variable-helper-btn:hover {
  background: linear-gradient(135deg, #5daf34 0%, #4e9a2a 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.4);
}

.file-name {
  font-size: 12px;
  color: #606266;
  margin-left: 8px;
}

.footer {
  padding: 8px;
  border-top: 1px solid #f5f7fa;
  background: #fafbfc;
}

/* 变量助手弹窗样式优化 */
.variable-helper-dialog {
  :deep(.el-dialog__body) {
    padding: 0 20px 20px 20px;
  }

  .variable-tabs {
    :deep(.el-tabs__header) {
      margin-bottom: 10px;
    }

    :deep(.el-tabs__nav-wrap) {
      padding: 0 10px;
    }

    :deep(.el-tabs__item) {
      padding: 0 16px;
      font-size: 14px;
      height: 40px;
      line-height: 40px;
    }

    :deep(.el-tabs__content) {
      overflow: hidden;
      height: 100%;
    }

    :deep(.el-tab-pane) {
      height: 100%;
    }
  }
}

:deep(.el-table) {
  font-size: 13px;
}

:deep(.el-table th) {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #303133;
}

:deep(.el-table td) {
  padding: 12px 0;
}

:deep(.el-table .cell) {
  padding: 0 10px;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}

:deep(.el-table__row.current-row) {
  background-color: #ecf5ff;
}

/* 全局 Header 参数区域样式 */
.global-headers-section {
  background: #ffffff;
  margin-top: 20px;
}

.global-headers-title {
  font-size: 13px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 12px;
  padding-left: 8px;
  border-left: 3px solid #67c23a;
}

.global-headers-editor {
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  background: #ffffff;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.global-headers-header {
  display: flex;
  background: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  padding: 12px 16px;
  font-weight: 600;
  font-size: 13px;
  color: #606266;

  .column {
    display: flex;
    align-items: center;
    padding: 0 8px;
    box-sizing: border-box;

    &:first-child {
      padding-left: 0;
    }

    &:last-child {
      padding-right: 0;
    }
  }

  .checkbox-column {
    width: 40px;
    min-width: 40px;
    padding: 0;
  }

  .key-column {
    width: 20%;
    min-width: 120px;
  }

  .value-column {
    width: 30%;
    min-width: 180px;
  }

  .type-column {
    width: 100px;
    min-width: 100px;
  }

  .description-column {
    width: 20%;
    min-width: 100px;
  }

  .action-column {
    width: 90px;
    min-width: 90px;
    justify-content: flex-end;
  }
}

.global-headers-list {
  .row {
    display: flex;
    border-bottom: 1px solid #f5f7fa;
    padding: 12px 16px;
    min-height: 56px;
    align-items: center;
    transition: all 0.25s ease;

    &:last-child {
      border-bottom: none;
    }

    &:hover {
      background: #f5f7fa;
    }

    &.disabled {
      opacity: 0.5;
      background: #fafafa;
    }

    .column {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 0 8px;
      box-sizing: border-box;

      &:first-child {
        padding-left: 0;
      }

      &:last-child {
        padding-right: 0;
      }
    }

    .checkbox-column {
      width: 40px;
      min-width: 40px;
      justify-content: center;
      padding: 0;
    }

    .key-column {
      width: 20%;
      min-width: 120px;
    }

    .value-column {
      width: 30%;
      min-width: 180px;
    }

    .type-column {
      width: 100px;
      min-width: 100px;
    }

    .description-column {
      width: 20%;
      min-width: 100px;
    }

    .action-column {
      width: 90px;
      min-width: 90px;
      justify-content: flex-end;
    }
  }
}

.global-hint {
  font-size: 12px;
  color: #909399;
  font-style: italic;
}
</style>