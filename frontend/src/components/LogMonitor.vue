<template>
  <el-card class="log-monitor-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <span class="title">实时日志监控</span>
        <el-button type="danger" size="small" @click="handleClose">关闭</el-button>
      </div>
    </template>

    <!-- 控制区域 -->
    <div class="controls-section">
      <div class="controls">
        <el-select v-model="selectedFile" placeholder="请选择日志文件" :disabled="isConnected" style="width: 300px;">
          <el-option
            v-for="file in logFiles"
            :key="file"
            :label="file"
            :value="file"
          ></el-option>
        </el-select>
        <el-button @click="fetchLogFiles" :loading="isFetchingFiles" :disabled="isConnected" :icon="Refresh" circle />
        <el-button @click="toggleConnection" :type="isConnected ? 'danger' : 'primary'" size="default">
          {{ isConnected ? '断开连接' : '开始监控' }}
        </el-button>
        <el-button @click="clearTerminal" type="warning" size="default" :disabled="!term">
          清屏
        </el-button>
        <div class="status-indicator" :class="{ connected: isConnected }">
          <div class="status-dot"></div>
          <span class="status-text">{{ isConnected ? '已连接' : '未连接' }}</span>
        </div>
      </div>

    </div>

    <!-- 日志显示区域 -->
    <div class="terminal-section">

      <div ref="terminalRef" class="terminal"></div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, defineProps, watch, defineEmits } from 'vue';
import { Refresh } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import 'xterm/css/xterm.css';
import { listLogFiles } from '@/api/closeApp';

const props = defineProps<{ lotId: string }>();
const emit = defineEmits(['close']);

const logFiles = ref<string[]>([]);
const selectedFile = ref<string>('');
const isConnected = ref(false);
const terminalRef = ref<HTMLElement | null>(null);
const isFetchingFiles = ref(false);
let term: Terminal;
let fitAddon: FitAddon;
let ws: WebSocket | null = null;
let isClosing = false; // 用于标记是否由关闭按钮触发的断开连接

const fetchLogFiles = async () => {
  isFetchingFiles.value = true;
  try {
    const response = await listLogFiles(props.lotId);
    logFiles.value = response.data;
    if (logFiles.value.length > 0) {
      // If there's no selected file or the selected file is not in the new list, select the first one.
      if (!selectedFile.value || !logFiles.value.includes(selectedFile.value)) {
        selectedFile.value = logFiles.value[0];
      }
    } else {
      selectedFile.value = ''; // No files, clear selection
    }
    ElMessage.success('日志文件列表已刷新');
  } catch (error) {
    ElMessage.error('刷新日志文件列表失败');
  } finally {
    isFetchingFiles.value = false;
  }
};

const toggleConnection = () => {
  if (isConnected.value) {
    disconnect();
  } else {
    connect();
  }
};

const connect = () => {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择一个日志文件');
    return;
  }

  const wsUrl = `ws://${window.location.hostname}:17771/closeApp/ws/log-monitor?lot_id=${props.lotId}&filename=${selectedFile.value}`;
  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    isConnected.value = true;
    term.clear();
    term.writeln(`连接成功，开始监控 ${selectedFile.value}...`);
  };

  const colorizeLogLine = (line: string) => {
  const reset = '\x1b[0m';
  const cyan = '\x1b[36m';      // For timestamp

  // Color mapping for log levels
  const levelColors: { [key: string]: string } = {
    info: '\x1b[32m',    // green
    warning: '\x1b[33m', // yellow
    warn: '\x1b[33m',    // yellow
    error: '\x1b[31m',   // red
    critical: '\x1b[31m',// red
    debug: '\x1b[34m',   // blue
  };

  const regex = /^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6})\s+([a-zA-Z]+)\s+(.*)$/;
  const match = line.match(regex);

  if (match) {
    const [, timestamp, level, message] = match;
    const lowerLevel = level.toLowerCase();
    const levelColor = levelColors[lowerLevel] || ''; // Default to no color if level not in map

    return `${cyan}${timestamp}${reset} ${levelColor}${level.padEnd(8)}${reset} ${message}`;
  }

  return line; // Return original line if it doesn't match the format
};

ws.onmessage = (event) => {
    // Assuming the backend might send multiple lines at once
    const lines = event.data.split(/\r\n|\n|\r/);
    const colorizedOutput = lines.map((line: string) => line ? colorizeLogLine(line) : '').join('\r\n');
    term.write(colorizedOutput);
  };

  ws.onclose = () => {
    isConnected.value = false;
    term.writeln('\n\n连接已断开');
    if (isClosing) {
      emit('close');
      isClosing = false; // 重置标志
    }
  };

  ws.onerror = (error) => {
    ElMessage.error('WebSocket 连接发生错误');
    console.error('WebSocket Error:', error);
  };
};

const disconnect = () => {
  if (ws) {
    ws.close();
  }
};

const clearTerminal = () => {
  if (term) {
    term.clear();
  }
};

const addNewLine = () => {
  if (term) {
    term.writeln('');
  }
};

const handleClose = () => {
  if (isConnected.value) {
    isClosing = true;
    disconnect();
  } else {
    emit('close');
  }
};

const fit = () => {
  try {
    fitAddon?.fit();
  } catch (e) {
    console.error('Terminal fit failed:', e);
  }
};

onMounted(() => {
  fetchLogFiles();
});

watch(terminalRef, (terminalEl) => {
  if (terminalEl && !term) {
    term = new Terminal({
      convertEol: true,
      scrollback: 1000,
      lineHeight: 1.25,
      theme: {
        background: '#282a36',
        foreground: '#f8f8f2',
        cursor: '#f8f8f2',
        selectionBackground: '#44475a',
        black: '#000000',
        red: '#ff5555',
        green: '#50fa7b',
        yellow: '#f1fa8c',
        blue: '#bd93f9',
        magenta: '#ff79c6',
        cyan: '#8be9fd',
        white: '#ffffff',
        brightBlack: '#6272a4',
        brightRed: '#ff6e6e',
        brightGreen: '#69ff94',
        brightYellow: '#ffffa5',
        brightBlue: '#d6acff',
        brightMagenta: '#ff92df',
        brightCyan: '#a4ffff',
        brightWhite: '#ffffff',
      },
    });
    fitAddon = new FitAddon();
    term.loadAddon(fitAddon);
    term.open(terminalEl);

    term.onKey(({ domEvent }) => {
      if (domEvent.key === 'Enter') {
        addNewLine();
      }
    });

    // 阻止在终端区域滚动时页面跟着滚动
    terminalEl.addEventListener('wheel', (event) => {
      const viewport = terminalEl.querySelector('.xterm-viewport') as HTMLElement;
      if (viewport) {
        const { scrollTop, scrollHeight, clientHeight } = viewport;
        const isScrollingDown = event.deltaY > 0;
        const isScrollingUp = event.deltaY < 0;

        // 当滚动到顶部且继续向上滚动时，阻止页面滚动
        if (scrollTop === 0 && isScrollingUp) {
          event.preventDefault();
          return;
        }

        // 当滚动到底部且继续向下滚动时，阻止页面滚动
        if (Math.ceil(scrollTop) + clientHeight >= scrollHeight && isScrollingDown) {
          event.preventDefault();
          return;
        }
      }
    }, { passive: false });

    // 延迟执行fit，确保DOM完全渲染
    setTimeout(() => fit(), 100);

    window.addEventListener('resize', fit);

    term.writeln('终端准备就绪，请选择文件并开始监控。');
  }
});

onUnmounted(() => {
  disconnect();
  window.removeEventListener('resize', fit);
});
</script>

<style scoped>
.log-monitor-card {
  width: 100%;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
  border-top: 2px solid #e6a23c; /* 警告色，与车辆管理卡片连接 */
  margin-top: 20px; /* 与上方卡片保持间距 */
}

.log-monitor-card :deep(.el-card__header) {
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-bottom: 1px solid #e4e7ed;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 16px;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title::before {
  content: "📊";
  font-size: 18px;
}

.controls-section {
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fafbfc;
}

.controls {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.current-file-info {
  display: flex;
  justify-content: flex-end;
}

.current-file {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  border: 1px solid #e5e7eb;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: #f3f4f6;
  border-radius: 20px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.status-indicator.connected {
  background: #ecfdf5;
  border-color: #10b981;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #ef4444;
  transition: background-color 0.3s ease;
}

.status-indicator.connected .status-dot {
  background-color: #10b981;
}

.status-text {
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
}

.status-indicator.connected .status-text {
  color: #065f46;
}

.terminal-section {
  background: #1f2937;
}

.terminal-header {
  padding: 12px 20px;
  background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
  border-bottom: 1px solid #4b5563;
  display: flex;
  align-items: center;
}

.terminal-title {
  font-size: 14px;
  font-weight: 600;
  color: #f9fafb;
  display: flex;
  align-items: center;
  gap: 8px;
}

.terminal-title::before {
  content: "💻";
  font-size: 16px;
}

.terminal {
  width: 100%;
  height: 600px;
  border: none;
  border-radius: 0;
  /* padding-top: 16px;    保留上下内边距 */
  /* padding-bottom: 16px; */
  background-color: #282a36;
  box-sizing: border-box;
  position: relative;
  overflow: hidden; /* 隐藏任何可能溢出的内容 */
}

/* 将左右内边距应用到xterm内部，让滚动条靠右 */
.terminal :deep(.xterm) {
  padding: 0 16px;
}

.log-monitor-card :deep(.el-card__body) {
  padding: 0;
}

/* 确保xterm终端内容不会溢出到滚动条区域 */
.terminal :deep(.xterm-viewport) {
  overflow-y: auto !important;
  scrollbar-width: thin;
  scrollbar-color: #6b7280 #374151;
}

.terminal :deep(.xterm-viewport)::-webkit-scrollbar {
  width: 8px;
}

.terminal :deep(.xterm-viewport)::-webkit-scrollbar-track {
  background: #374151;
  border-radius: 4px;
}

.terminal :deep(.xterm-viewport)::-webkit-scrollbar-thumb {
  background: #6b7280;
  border-radius: 4px;
}

.terminal :deep(.xterm-viewport)::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .controls {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .terminal {
    height: 400px;
    padding-right: 24px;
  }

  .current-file-info {
    justify-content: center;
    margin-top: 8px;
  }
}
</style>

