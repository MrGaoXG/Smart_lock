/* global AMap */

<template>
  <canvas id="particle-canvas"></canvas>

  <div v-if="showWarning" class="geofence-warning">
    <div class="warning-content">
      <div class="warning-icon">⚠️</div>
      <div class="warning-text">
        <h3>超出电子围栏警告</h3>
        <p>您已离开安全区域，设备已自动上锁！</p>
      </div>
      <button class="warning-close" @click="dismissWarning">知道了</button>
    </div>
  </div>

  <div id="app">
    <header class="header">
      <div class="title-group">
        <h1>智能车锁 · 仪表盘看板</h1>
        <p>数字化监控中心 · {{ currentPageName }}</p>
      </div>
      
      <div class="style-switcher" v-if="currentPage === 'dashboard'">
        <div
          v-for="(s, k) in mapStyles"
          :key="k"
          class="style-dot"
          :style="{ background: s.dot }"
          :class="{ active: currentMapStyle === k }"
          @click="changeMapStyle(k)"
        ></div>
        <span style="font-size: 12px; min-width: 80px; text-align: center">
          {{ mapStyles[currentMapStyle].name }}
        </span>
      </div>

      <div style="text-align: right; font-size: 12px;">
        <div>设备ID：<b>{{ deviceId }}</b></div>
        <div style="opacity: 0.6">更新：{{ lastActive }}</div>
      </div>
    </header>

    <main class="page-container">
      <div class="dashboard-grid" v-show="currentPage === 'dashboard'">
        <div class="left-side">
          <div class="card">
            <div class="route-planner">
              <div style="font-size: 11px; color:var(--text-dim); margin-bottom: 5px;">智能导航 (Driving)</div>
              <input class="route-input" v-model="routeStart" placeholder="起点 (例如: 北京西站)">
              <input class="route-input" v-model="routeEnd" placeholder="终点 (例如: 天安门广场)">
              <button class="btn-go" @click="planRoute">开始规划路线</button>
            </div>

            <div class="map-tools">
              <button class="tool-btn" :class="{active: is3D}" @click="setMapView('3D')">3D</button>
              <button class="tool-btn" :class="{active: !is3D}" @click="setMapView('2D')">2D</button>
            </div>
            <div id="map-container"></div>
          </div>
          
          <div class="card panel status-panel">
            <div class="status-group">
              <div style="font-size: 14px; font-weight: bold; margin-bottom: 8px">状态快照</div>
              <div class="grid-info">
                <div class="info-tile"><label>电量</label><span>{{ battery }}%</span></div>
                <div class="info-tile"><label>信号</label><span>{{ signal }}/5</span></div>
                <div class="info-tile"><label>围栏状态</label><span :style="{color: isOutsideGeofence ? '#ff2a2a' : 'var(--accent)'}">{{ isOutsideGeofence ? '超出' : '安全' }}</span></div>
                <div class="info-tile"><label>围栏半径</label><span>{{ geofenceRadius }}m</span></div>
              </div>
            </div>
            <div class="status-center">
              <div style="font-size: 11px; opacity: 0.6">当前坐标</div>
              <div style="font-size: 13px; margin: 4px 0">{{ lat.toFixed(5) }}, {{ lng.toFixed(5) }}</div>
              <button class="btn-outline" style="padding: 6px 15px" @click="resetMap">定位车辆</button>
            </div>
            <div class="status-right">
              <div style="font-size: 11px; opacity: 0.6">实时时速</div>
              <div style="font-size: 26px; font-weight: 800; color: var(--accent)">{{ speed }} <small style="font-size: 12px">km/h</small></div>
            </div>
          </div>
        </div>

        <aside class="right-side">
          <div class="card panel" @click="changePage('lock')" style="cursor: pointer; border-color: var(--accent);">
            <div class="panel-hd">锁控中心 (点击详情) ↗</div>
            <div style="display: flex; align-items: center; gap: 15px">
              <div style="font-size: 32px">{{ locked ? '🔐' : '🔓' }}</div>
              <div>
                <div style="font-weight: bold; font-size: 16px">{{ locked ? '设备已上锁' : '设备已解锁' }}</div>
                <div style="font-size: 12px; color: #00ffa6">安全系统：运行中</div>
              </div>
            </div>
          </div>

          <div class="card panel">
            <div class="panel-hd">锁体健康仪表</div>
            <div class="gauge-wrap">
              <svg viewBox="0 0 100 100" style="width:100%; height:100%; transform: rotate(-90deg);">
                <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="6"></circle>
                <circle cx="50" cy="50" r="45" fill="none" stroke="var(--accent)" stroke-width="6"
                        stroke-dasharray="283" :stroke-dashoffset="283 - (283 * health / 100)"
                        stroke-linecap="round" style="transition: 1s ease-out"></circle>
              </svg>
              <div class="gauge-text">
                <span class="big">{{ health }}%</span>
                <span class="sml">设备健康度</span>
              </div>
            </div>
            <div class="lock-button-container">
              <button class="btn-action" @click.stop="handleLock">远程{{ locked ? '解锁' : '上锁' }}</button>
            </div>
          </div>

          <div class="card panel">
            <div class="panel-hd">环境指标</div>
            <div class="grid-info">
              <div class="info-tile"><label>环境温度</label><span>{{ temp }}°C</span></div>
              <div class="info-tile"><label>累计里程</label><span>{{ mileage }}km</span></div>
            </div>
          </div>

          <div class="card panel">
            <div class="panel-hd">行驶统计</div>
            <div style="font-size: 13px">今日累计：{{ dayDist }} km</div>
            <div class="progress-container">
              <div class="bar-bg"><div class="bar-fill" :style="{width: (dayDist/50*100)+'%'}"></div></div>
            </div>
            <div style="font-size: 10px; opacity: 0.5; margin-top: 6px">目标里程 50 km</div>
          </div>

          <div class="card panel">
            <div class="panel-hd">电子围栏设置</div>
            <div style="margin-bottom: 15px">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <label style="font-size: 12px; color: var(--text-dim);">围栏半径</label>
                <span style="font-size: 16px; font-weight: bold; color: var(--accent);">{{ geofenceRadius }}m</span>
              </div>
              <input 
                type="range" 
                v-model="geofenceRadius" 
                min="100" 
                max="2000" 
                step="50"
                @input="updateGeofenceRadius"
                style="width: 100%; cursor: pointer;"
              >
              <div style="display: flex; justify-content: space-between; font-size: 10px; opacity: 0.5; margin-top: 4px;">
                <span>100m</span>
                <span>2000m</span>
              </div>
            </div>
            <div style="font-size: 11px; opacity: 0.6; line-height: 1.5;">
              设置设备的安全活动范围，当用户超出此范围时将自动上锁。
            </div>
          </div>
        </aside>
      </div>

      <div class="sub-page" v-if="currentPage === 'lock'">
        <div class="card panel full-width">
          <div class="panel-hd">锁体结构透视</div>
          <div style="display: flex; justify-content: space-around; align-items: center; padding: 20px;">
            <div style="width: 200px; height: 120px; border: 2px solid var(--accent); border-radius: 10px; position: relative; display: flex; align-items: center; justify-content: center; background: rgba(0, 234, 255, 0.05);">
              <div :style="{width: locked ? '60px' : '0px'}" style="height: 20px; background: var(--accent); transition: 0.5s; position: absolute; left: 10px; border-radius: 4px;"></div>
              <span style="font-size: 12px; color: var(--accent); z-index: 2;">{{ locked ? 'LOCKED' : 'UNLOCKED' }}</span>
              <div style="position: absolute; right: 20px; top: 10px; width: 10px; height: 10px; background: #ff2a2a; border-radius: 50%; box-shadow: 0 0 10px #ff2a2a;"></div>
            </div>
            <div style="text-align: left; font-size: 12px; line-height: 2;">
              <div>主控芯片: <span style="color:var(--accent)">运行正常</span></div>
              <div>蓝牙模块: <span style="color:var(--accent)">连接中 (BLE 5.0)</span></div>
              <div>机械传动: <span style="color:var(--accent)">无卡滞</span></div>
            </div>
          </div>
        </div>

        <div class="card panel">
          <div class="panel-hd">传感器实时数据</div>
          <div class="detail-item"><span>电机温度</span><span class="detail-value">{{ sensors.motor_temp }}°C</span></div>
          <div class="detail-item"><span>实时扭矩</span><span class="detail-value">{{ sensors.torque }} N·m</span></div>
          <div class="detail-item"><span>输入电压</span><span class="detail-value">{{ sensors.voltage }} V</span></div>
          <div class="detail-item"><span>输入电流</span><span class="detail-value">{{ sensors.current }} A</span></div>
          <div class="detail-item"><span>震动监测</span><span class="detail-value">{{ sensors.vibration }}</span></div>
          <div class="detail-item"><span>霍尔状态</span><span class="detail-value">{{ sensors.hall_status }}</span></div>
        </div>

        <div class="card panel">
          <div class="panel-hd">使用寿命统计</div>
          <div class="detail-item"><span>激活日期</span><span class="detail-value">{{ sensors.activ_time }}</span></div>
          <div class="detail-item"><span>通电时长</span><span class="detail-value">{{ sensors.total_usage }}</span></div>
          <div class="detail-item"><span>开关次数</span><span class="detail-value">1,248 次</span></div>
          <div class="detail-item"><span>最近维护</span><span class="detail-value">2026/01/01</span></div>
        </div>
        
        <button class="btn-action full-width" @click="handleLock">执行远程诊断 (同时{{ locked ? '解锁' : '上锁' }})</button>
      </div>

      <div class="sub-page" v-if="currentPage === 'settings'">
        <div class="full-width">
          <div class="user-card">
            <div class="avatar">👨‍🚀</div>
            <div>
              <div style="font-size: 20px; font-weight: bold; color: var(--accent);">{{ user.username }}</div>
              <div style="font-size: 12px; color: var(--text-dim);">{{ user.role }} · ID: {{ deviceId }}</div>
            </div>
            <div style="margin-left: auto;">
              <button class="btn-outline">编辑资料</button>
            </div>
          </div>
        </div>

        <div class="card panel">
          <div class="panel-hd">应用偏好</div>
          <div class="detail-item">
            <span>推送通知</span>
            <div class="style-dot active"></div>
          </div>
          <div class="detail-item">
            <span>自动上锁 (离车3米)</span>
            <div class="style-dot active"></div>
          </div>
          <div class="detail-item">
            <span>声音反馈</span>
            <div class="style-dot"></div>
          </div>
        </div>

        <div class="card panel">
          <div class="panel-hd">关于产品</div>
          <div class="detail-item"><span>固件版本</span><span class="detail-value">{{ user.version }}</span></div>
          <div class="detail-item"><span>硬件型号</span><span class="detail-value">Titan-Lock Gen2</span></div>
          <div class="detail-item"><span>开发者</span><span class="detail-value">Flask Framework Inc.</span></div>
          <div style="padding: 12px; font-size: 11px; opacity: 0.5;">
            © 2026 智能车锁系统 版权所有。<br>
            本系统遵循 MIT 开源协议。
          </div>
        </div>
      </div>
    </main>

    <footer class="bottom-nav">
      <div class="nav-item" :class="{active: currentPage === 'dashboard'}" @click="changePage('dashboard')">首页看板</div>
      <div class="nav-item" :class="{active: currentPage === 'lock'}" @click="changePage('lock')">锁状态</div>
      <div class="nav-item" :class="{active: currentPage === 'settings'}" @click="changePage('settings')">我的设置</div>
    </footer>

    <div class="fab-group" v-show="currentPage === 'dashboard'">
      <div class="fab large" @click="handleLock">{{ locked ? '🔐' : '🔓' }}</div>
      <div class="fab" title="回正视图" @click="resetMap">📍</div>
      <div class="fab" title="设置" @click="changePage('settings')">⚙️</div>
      <div class="fab" title="AI助手" @click="toggleChat">🤖</div>
    </div>
    
    <!-- AI Chat Window -->
    <div class="chat-window" v-if="showChat">
      <div class="chat-header">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="font-size: 20px;">🤖</span>
          <span style="font-weight: bold;">智能车锁AI助手</span>
        </div>
        <button class="close-btn" @click="toggleChat">×</button>
      </div>
      <div class="chat-body" ref="chatBody">
        <div v-for="(msg, index) in chatMessages" :key="index" class="message" :class="msg.role">
          <div class="message-content">{{ msg.content }}</div>
        </div>
        <div v-if="isTyping" class="message assistant">
          <div class="message-content typing">...</div>
        </div>
      </div>
      <div class="chat-footer">
        <input 
          v-model="userInput" 
          @keyup.enter="sendMessage" 
          placeholder="输入问题，例如：如何远程解锁？" 
          type="text"
        >
        <button class="voice-btn" @click="startVoiceInput" :class="{ 'recording': isRecording }" title="按住说话">
          {{ isRecording ? '🎙️...' : '🎙️' }}
        </button>
        <button @click="sendMessage" :disabled="isTyping || !userInput.trim()">发送</button>
      </div>
    </div>
  </div>
</template>

<script>
/* global AMap */
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';

const api = axios.create({
  // 生产环境使用 Nginx 转发，这里留空即可，因为请求本身就包含了 /api 前缀
  // 比如请求 '/api/chat'，浏览器会自动补全为 'https://zixianggao.icu/api/chat'
  baseURL: process.env.NODE_ENV === 'production' ? '' : 'http://localhost:5000',
  timeout: 5000
});

export default {
  name: 'App',
  setup() {
    const currentPage = ref('dashboard');
    const changePage = (page) => (currentPage.value = page);
    const currentPageName = computed(() => {
      if (currentPage.value === 'dashboard') return '实时监控';
      if (currentPage.value === 'lock') return '硬件详情';
      return '用户中心';
    });

    const deviceId = ref('X1-Pro-0092A');
    const locked = ref(true);
    const battery = ref(83);
    const signal = ref(4);
    const lat = ref(39.909187);
    const lng = ref(116.397451);
    const health = ref(92);
    const temp = ref(28);
    const mileage = ref(312.6);
    const dayDist = ref(6.40);
    const lastActive = ref('2026/01/18 17:17:31');
    const speed = ref(0);

    const sensors = ref({
      motor_temp: 34.2,
      torque: 1.2,
      voltage: 48.2,
      current: 0.05,
      vibration: 'Safe',
      hall_status: 'Normal',
      activ_time: '2025/06/15',
      total_usage: '142h 20m'
    });

    const user = ref({
      username: 'CyberRider_01',
      role: 'Administrator',
      avatar_emoji: '👨‍🚀',
      version: 'v3.1.0 (Beta)'
    });

    const is3D = ref(true);
    const currentMapStyle = ref('darkblue');
    const mapStyles = {
      darkblue: { name: '深蓝极客', dot: '#06cfff', url: 'amap://styles/darkblue' },
      grey: { name: '灰阶模式', dot: '#9ea7ad', url: 'amap://styles/grey' },
      fresh: { name: '清新自然', dot: '#37b8ff', url: 'amap://styles/fresh' }
    };

    const routeStart = ref('');
    const routeEnd = ref('');
    let map, marker, driving, geofenceCircle, userMarker;

    const geofenceRadius = ref(parseInt(localStorage.getItem('geofenceRadius')) || 500);
    const userLat = ref(39.909187);
    const userLng = ref(116.397451);
    const isOutsideGeofence = ref(false);
    const showWarning = ref(false);
    const geofenceEnabled = ref(true);

    const showChat = ref(false);
    const userInput = ref('');
    const chatMessages = ref([
      { role: 'assistant', content: '你好！我是你的智能车锁AI助手，有什么可以帮你的吗？' }
    ]);
    const isTyping = ref(false);
    const chatBody = ref(null);

    const toggleChat = () => {
      showChat.value = !showChat.value;
      if (showChat.value) {
        setTimeout(scrollToBottom, 100);
      }
    };

    const scrollToBottom = () => {
      if (chatBody.value) {
        chatBody.value.scrollTop = chatBody.value.scrollHeight;
      }
    };

    const isRecording = ref(false);

    // 语音识别
    const startVoiceInput = () => {
      if (!('webkitSpeechRecognition' in window)) {
        alert('您的浏览器不支持语音识别，请使用 Chrome 或 Edge。');
        return;
      }
      
      const recognition = new window.webkitSpeechRecognition();
      recognition.lang = 'zh-CN';
      recognition.continuous = false;
      recognition.interimResults = false;
      
      recognition.onstart = () => {
        isRecording.value = true;
      };
      
      recognition.onend = () => {
        isRecording.value = false;
      };
      
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        userInput.value = transcript;
        // 可选：识别完成后自动发送
        // sendMessage(); 
      };
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        isRecording.value = false;
      };
      
      recognition.start();
    };

    let typeWriterTimer = null;
    let currentTypingMessage = null;
    let currentFullText = '';
    let latestNavigationTimestamp = 0;

    // 打字机效果函数
    const typeWriterEffect = (text, targetMessage) => {
      // 如果有正在进行的打字任务，先立即完成它
      if (typeWriterTimer) {
        clearInterval(typeWriterTimer);
        if (currentTypingMessage) {
          currentTypingMessage.content = currentFullText;
        }
      }

      let i = 0;
      isTyping.value = true;
      targetMessage.content = ''; // 清空初始内容
      
      currentTypingMessage = targetMessage;
      currentFullText = text;
      
      typeWriterTimer = setInterval(() => {
        if (i < text.length) {
          targetMessage.content += text.charAt(i);
          i++;
          scrollToBottom();
        } else {
          clearInterval(typeWriterTimer);
          typeWriterTimer = null;
          currentTypingMessage = null;
          isTyping.value = false;
        }
      }, 30); // 每个字符间隔30ms
    };

    const sendMessage = async () => {
      // 如果正在打字，立即中断并显示完整内容
      if (isTyping.value) {
        if (typeWriterTimer) {
          clearInterval(typeWriterTimer);
          typeWriterTimer = null;
        }
        if (currentTypingMessage) {
          currentTypingMessage.content = currentFullText;
          currentTypingMessage = null;
        }
        isTyping.value = false;
      }

      const message = userInput.value.trim();
      if (!message) return;

      chatMessages.value.push({ role: 'user', content: message });
      userInput.value = "";
      isTyping.value = true;
      scrollToBottom();

      try {
        // 准备发送给后端的历史记录
        const historyToSend = chatMessages.value.map(msg => ({
          role: msg.role,
          content: msg.content
        }));

        const res = await api.post('/api/chat', { 
          message,
          history: historyToSend 
        });
        
        let reply = res.data.reply;

        // 处理导航指令 [CMD:NAV:目的地]
        const navMatch = reply.match(/\[CMD:NAV:(.*?)\]/);
        if (navMatch) {
          const destination = navMatch[1];
          reply = reply.replace(navMatch[0], ''); // 移除指令文本
          
          // 立即触发导航，不等待打字机
          startAiNavigation(destination);
          
          // 创建一个新的助手消息用于显示回复文本
          const aiMsg = { role: 'assistant', content: '' };
          chatMessages.value.push(aiMsg);
          const targetMsg = chatMessages.value[chatMessages.value.length - 1];
          
          if (reply.trim()) {
            typeWriterEffect(reply, targetMsg);
          } else {
            // 如果只有指令没有文本，移除空消息
            chatMessages.value.pop();
            isTyping.value = false;
          }
        } else {
          // 普通回复，使用打字机效果
          const aiMsg = { role: 'assistant', content: '...' }; // 占位符
          chatMessages.value.push(aiMsg);
          // 获取数组中的响应式对象
          const targetMsg = chatMessages.value[chatMessages.value.length - 1];
          typeWriterEffect(reply, targetMsg);
        }
        
        // AI可能更改了设备状态，刷新数据
        await fetchData();
      } catch (e) {
        chatMessages.value.push({ role: 'assistant', content: '抱歉，网络连接异常，请稍后再试。' });
        isTyping.value = false;
        scrollToBottom();
      }
    };

    const fetchData = async () => {
      try {
        const res = await api.get('/api/device');
        const data = res.data;
        deviceId.value = data.device_id;
        locked.value = data.is_locked;
        battery.value = data.battery;
        signal.value = data.signal;
        lat.value = data.lat;
        lng.value = data.lng;
        health.value = data.health;
        temp.value = data.temp;
        mileage.value = data.mileage;
        dayDist.value = data.day_dist;
        lastActive.value = data.last_action_time;
        sensors.value = data.sensors || {};
        user.value = data.user_info || {};
      } catch (e) {
        console.error('Failed to fetch device data:', e);
      }
    };

    const initMap = () => {
      if (!window.AMap) {
        console.error('AMap not loaded');
        return;
      }
      
      map = new AMap.Map('map-container', {
        viewMode: '3D',
        pitch: 50,
        zoom: 16,
        center: [lng.value, lat.value],
        mapStyle: mapStyles[currentMapStyle.value].url
      });

      marker = new AMap.Marker({
        position: [lng.value, lat.value],
        content: `<div style="width:24px;height:24px;background:var(--accent);border:2px solid #fff;border-radius:50%;box-shadow:0 0 15px var(--accent);"></div>`,
        offset: new AMap.Pixel(-12, -12)
      });
      map.add(marker);

      geofenceCircle = new AMap.Circle({
        center: [lng.value, lat.value],
        radius: geofenceRadius.value,
        strokeColor: '#00eaff',
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: '#00eaff',
        fillOpacity: 0.15
      });
      map.add(geofenceCircle);

      userMarker = new AMap.Marker({
        position: [userLat.value, userLng.value],
        content: `<div style="width:20px;height:20px;background:#ff2a2a;border:2px solid #fff;border-radius:50%;box-shadow:0 0 10px #ff2a2a;"></div>`,
        offset: new AMap.Pixel(-10, -10)
      });
      map.add(userMarker);

      // 显式加载Driving和PlaceSearch插件
      AMap.plugin(['AMap.Driving', 'AMap.PlaceSearch'], function () {
        console.log('AMap plugins loaded');
        driving = new AMap.Driving({
          map: map,
          policy: AMap.DrivingPolicy.LEAST_TIME
        });
        console.log('Driving object created:', driving);
      });
    };

    const startAiNavigation = (destination) => {
      const thisNavigationTimestamp = Date.now();
      latestNavigationTimestamp = thisNavigationTimestamp;

      console.log('Starting navigation to:', destination);
      
      // 更新UI绑定的输入框
      routeEnd.value = destination;
      routeStart.value = "当前位置";
      
      chatMessages.value.push({ role: 'assistant', content: `正在为您规划前往 ${destination} 的路线...` });
      scrollToBottom();

      // 1. 确保 Driving 实例存在且唯一
      if (!driving) {
        if (window.AMap && map) {
          driving = new AMap.Driving({
            map: map,
            policy: AMap.DrivingPolicy.LEAST_TIME,
            hideMarkers: false, // 显示起终点标记
            showTraffic: false  // 不显示路况
          });
        } else {
          chatMessages.value.push({ role: 'assistant', content: '地图组件尚未就绪，请稍后重试。' });
          return;
        }
      }

      // 2. 无论是否是新实例，都先清除地图上的旧路线
      driving.clear();

      // 3. 使用 PlaceSearch 获取目的地坐标
      const placeSearch = new AMap.PlaceSearch({
        pageSize: 1,
        extensions: 'base'
      });

      placeSearch.search(destination, function(status, result) {
        // 检查是否是最新的请求
        if (latestNavigationTimestamp !== thisNavigationTimestamp) {
          console.log('Navigation request cancelled (superseded by new request).');
          return;
        }

        if (status === 'complete' && result.info === 'OK' && result.poiList && result.poiList.pois && result.poiList.pois.length > 0) {
          const poi = result.poiList.pois[0];
          const endLngLat = poi.location;
          
          console.log(`Found destination: ${poi.name} at ${endLngLat}`);
          
          // 4. 执行路径规划
          driving.search(
            new AMap.LngLat(lng.value, lat.value),
            endLngLat,
            function(status, result) {
              if (status === 'complete') {
                const distance = (result.routes[0].distance / 1000).toFixed(1);
                const time = (result.routes[0].time / 60).toFixed(0);
                chatMessages.value.push({ 
                  role: 'assistant', 
                  content: `路径规划成功！\n目的地：${poi.name}\n全程：${distance}公里\n预计耗时：${time}分钟` 
                });
              } else {
                console.error('Driving search failed:', status, result);
                chatMessages.value.push({ role: 'assistant', content: `抱歉，无法规划到 ${destination} 的驾车路线（错误代码：${status}）。` });
              }
              scrollToBottom();
            }
          );
        } else {
          console.error('Place search failed:', status, result);
          chatMessages.value.push({ role: 'assistant', content: `抱歉，找不到地点 "${destination}"。` });
          scrollToBottom();
        }
      });
    };

    const planRoute = () => {
      console.log('planRoute function called');
      console.log('routeStart:', routeStart.value);
      console.log('routeEnd:', routeEnd.value);
      console.log('driving object:', driving);
      console.log('AMap.DrivingPolicy:', AMap.DrivingPolicy);
      
      if (!routeStart.value || !routeEnd.value) {
        alert('请输入起点和终点');
        return;
      }
      if (!driving) {
        alert('路径规划功能不可用，请检查高德地图API加载状态');
        return;
      }
      
      try {
        console.log('Clearing previous route');
        driving.clear();
        
        console.log('Starting route planning');
        
        // 尝试使用更简单的调用方式
        driving.search([
          {
            keyword: routeStart.value,
            city: '北京'
          },
          {
            keyword: routeEnd.value,
            city: '北京'
          }
        ], function(status, result) {
            console.log('Driving search callback:', status, result);
            if (status === 'complete') {
              if (result.routes && result.routes.length > 0) {
                console.log('路径规划成功:', result.routes[0]);
                alert('路径规划成功！');
              } else {
                alert('未找到相关路径，请检查输入地址');
              }
            } else {
              console.error('路径规划失败:', status, result);
              let errorMessage = '路径规划失败，请检查网络连接或输入地址';
              
              // 处理常见错误
              if (status === 'error') {
                if (result && result.info) {
                  errorMessage = `路径规划失败: ${result.info}`;
                }
                if (result && result.code === 'INVALID_USER_KEY') {
                  errorMessage = '路径规划失败: API Key无效，请检查高德地图API Key配置';
                }
              }
              
              alert(errorMessage);
            }
          });
      } catch (error) {
        console.error('Error in planRoute:', error);
        alert('路径规划过程中发生错误: ' + error.message);
      }
    };

    const setMapView = (mode) => {
      is3D.value = mode === '3D';
      map.setPitch(is3D.value ? 50 : 0, false, 600);
      if (!is3D.value) map.setRotation(0, false, 600);
    };

    const changeMapStyle = (key) => {
      currentMapStyle.value = key;
      map.setMapStyle(mapStyles[key].url);
    };

    const resetMap = () => map.setCenter([lng.value, lat.value]);

    const handleLock = async () => {
      const action = locked.value ? 'unlock' : 'lock';
      try {
        const res = await api.post('/api/control', { action });
        locked.value = res.data.is_locked;
        lastActive.value = res.data.time;
        alert(`${action === 'lock' ? '上锁' : '解锁'}操作成功！`);
      } catch (e) {
        console.error('Lock control error:', e);
        alert('操作失败，请检查后端服务是否正常运行');
      }
    };

    const calculateDistance = (lat1, lng1, lat2, lng2) => {
      const R = 6371000;
      const dLat = (lat2 - lat1) * Math.PI / 180;
      const dLng = (lng2 - lng1) * Math.PI / 180;
      const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                Math.sin(dLng / 2) * Math.sin(dLng / 2);
      const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
      return R * c;
    };

    const checkGeofence = () => {
      if (!geofenceEnabled.value) return;
      
      const distance = calculateDistance(
        lat.value, lng.value,
        userLat.value, userLng.value
      );
      
      const wasOutside = isOutsideGeofence.value;
      isOutsideGeofence.value = distance > geofenceRadius.value;
      
      if (isOutsideGeofence.value && !wasOutside) {
        showWarning.value = true;
        autoLock();
      }
      
      if (geofenceCircle) {
        geofenceCircle.setCenter([lng.value, lat.value]);
      }
      
      if (userMarker) {
        userMarker.setPosition([userLng.value, userLat.value]);
      }
    };

    const updateGeofenceRadius = () => {
      if (geofenceCircle) {
        geofenceCircle.setRadius(geofenceRadius.value);
      }
      localStorage.setItem('geofenceRadius', geofenceRadius.value);
      checkGeofence();
    };

    const autoLock = async () => {
      if (!locked.value) {
        try {
          await api.post('/api/control', { action: 'lock' });
          locked.value = true;
          lastActive.value = new Date().toLocaleString('zh-CN');
        } catch (e) {
          console.error('Auto lock error:', e);
        }
      }
    };

    const simulateUserMovement = () => {
      const directions = [
        { lat: 0.001, lng: 0 },
        { lat: -0.001, lng: 0 },
        { lat: 0, lng: 0.001 },
        { lat: 0, lng: -0.001 },
        { lat: 0.0007, lng: 0.0007 },
        { lat: -0.0007, lng: -0.0007 }
      ];
      
      setInterval(() => {
        const direction = directions[Math.floor(Math.random() * directions.length)];
        userLat.value += direction.lat;
        userLng.value += direction.lng;
        checkGeofence();
      }, 2000);
    };

    const dismissWarning = () => {
      showWarning.value = false;
    };

    const initParticles = () => {
      const canvas = document.getElementById('particle-canvas');
      const ctx = canvas.getContext('2d');
      let w = (canvas.width = window.innerWidth);
      let h = (canvas.height = window.innerHeight);
      
      window.addEventListener('resize', () => {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
      });

      let pts = [];
      for (let i = 0; i < 40; i++)
        pts.push({ x: Math.random() * w, y: Math.random() * h, vx: Math.random() - 0.5, vy: Math.random() - 0.5 });

      const draw = () => {
        ctx.clearRect(0, 0, w, h);
        ctx.fillStyle = 'rgba(0, 234, 255, 0.3)';
        pts.forEach((p) => {
          p.x += p.vx;
          p.y += p.vy;
          if (p.x < 0 || p.x > w) p.vx *= -1;
          if (p.y < 0 || p.y > h) p.vy *= -1;
          ctx.beginPath();
          ctx.arc(p.x, p.y, 1, 0, Math.PI * 2);
          ctx.fill();
        });
        requestAnimationFrame(draw);
      };
      draw();
    };

    onMounted(() => {
      fetchData();
      initMap();
      initParticles();
      simulateUserMovement();
      
      // 模拟速度变化
      setInterval(() => {
        speed.value = locked.value ? 0 : (Math.random() * 6).toFixed(1);
      }, 3000);

      // 定时轮询后端数据 (每3秒一次)
      setInterval(() => {
        fetchData();
      }, 3000);
    });

    return {
      currentPage,
      changePage,
      currentPageName,
      deviceId,
      locked,
      battery,
      signal,
      lat,
      lng,
      health,
      temp,
      mileage,
      dayDist,
      lastActive,
      speed,
      sensors,
      user,
      currentMapStyle,
      mapStyles,
      is3D,
      setMapView,
      changeMapStyle,
      handleLock,
      resetMap,
      routeStart,
      routeEnd,
      planRoute,
      geofenceRadius,
      isOutsideGeofence,
      showWarning,
      geofenceEnabled,
      dismissWarning,
      updateGeofenceRadius,
      showChat,
      toggleChat,
      userInput,
      chatMessages,
      sendMessage,
      isTyping,
      isRecording,
      startVoiceInput,
      chatBody,
      startAiNavigation
    };
  }
};
</script>

<style>
/* AI Chat Styles */
.chat-window {
  position: fixed;
  bottom: 100px;
  right: 30px;
  width: 350px;
  height: 500px;
  background: var(--bg-panel);
  border: 1px solid var(--accent);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  z-index: 200;
  box-shadow: 0 0 30px rgba(0, 234, 255, 0.2);
  backdrop-filter: blur(15px);
  overflow: hidden;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.chat-header {
  padding: 15px;
  background: rgba(0, 234, 255, 0.1);
  border-bottom: 1px solid rgba(0, 234, 255, 0.2);
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--accent);
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-dim);
  font-size: 24px;
  cursor: pointer;
  line-height: 1;
}

.chat-body {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  display: flex;
  max-width: 85%;
}

.message.user {
  align-self: flex-end;
}

.message.assistant {
  align-self: flex-start;
}

.message-content {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 13px;
  line-height: 1.5;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message.user .message-content {
  background: var(--accent);
  color: #000;
  border-top-right-radius: 2px;
}

.message.assistant .message-content {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-main);
  border-top-left-radius: 2px;
}

.chat-footer {
  padding: 15px;
  border-top: 1px solid rgba(0, 234, 255, 0.2);
  display: flex;
  gap: 10px;
}

.chat-footer input {
  flex: 1;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(0, 234, 255, 0.3);
  border-radius: 6px;
  padding: 8px 12px;
  color: #fff;
  font-size: 13px;
  outline: none;
}

.chat-footer input:focus {
  border-color: var(--accent);
}

.chat-footer button {
  background: var(--accent);
  color: #000;
  border: none;
  border-radius: 6px;
  padding: 0 15px;
  font-weight: bold;
  cursor: pointer;
  font-size: 13px;
}

.chat-footer button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 录音按钮样式 */
.voice-btn {
  background: transparent !important;
  border: 1px solid var(--accent) !important;
  color: var(--accent) !important;
  font-size: 16px !important;
  padding: 0 10px !important;
  transition: all 0.3s ease;
  min-width: 40px;
}

.voice-btn.recording {
  background: rgba(255, 0, 0, 0.2) !important;
  border-color: #ff2a2a !important;
  color: #ff2a2a !important;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

/* 移动端适配 Chat */
@media (max-width: 767px) {
  .chat-window {
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    height: 100%;
    border-radius: 0;
    z-index: 1000;
  }
}

:root {
  --bg-dark: #05121a;
  --bg-panel: rgba(7, 35, 50, 0.85);
  --accent: #00eaff;
  --accent-glow: rgba(0, 234, 255, 0.35);
  --border: rgba(0, 234, 255, 0.25);
  --text-main: #eafcff;
  --text-dim: #9bdff6;
  --danger: #ff2a2a;
}

* { box-sizing: border-box; }
body, html { margin: 0; padding: 0; height: 100%; background: var(--bg-dark); color: var(--text-main); font-family: "Inter", "Segoe UI", sans-serif; }

#particle-canvas { position: fixed; inset: 0; z-index: 0; opacity: 0.25; pointer-events: none; }
#app { position: relative; z-index: 1; display: flex; flex-direction: column; min-height: 100vh; height: 100%; padding: 12px 18px; overflow: hidden; }

/* 响应式设计 */
/* 大屏幕桌面 */
@media (min-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr 420px;
  }
}

/* 中等屏幕桌面 */
@media (max-width: 1199px) and (min-width: 992px) {
  .dashboard-grid {
    grid-template-columns: 1fr 380px;
  }
}

/* 小屏幕桌面/平板 */
@media (max-width: 991px) and (min-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr 320px;
  }
  
  .left-side {
    grid-template-rows: 400px auto;
  }
  
  .route-planner {
    width: 220px;
  }
}

/* 平板设备 */
@media (max-width: 767px) and (min-width: 640px) {
  #app {
    padding: 10px 14px;
    height: 100%;
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }
  
  .left-side {
    grid-template-rows: 380px auto;
  }
  
  .right-side {
    max-height: 450px;
  }
  
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .style-switcher {
    margin-top: 8px;
  }
  
  .title-group h1 {
    font-size: 17px;
  }
  
  .route-planner {
    width: 200px;
  }
  
  .grid-info {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
}

/* 大屏手机 */
@media (max-width: 639px) and (min-width: 480px) {
  #app {
    padding: 8px 12px;
    height: 100%;
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }
  
  .left-side {
    grid-template-rows: 350px auto;
  }
  
  .right-side {
    max-height: 400px;
  }
  
  .title-group h1 {
    font-size: 16px;
  }
  
  .route-planner {
    width: 180px;
    padding: 9px;
  }
  
  .route-input {
    font-size: 11px;
    padding: 5px 8px;
  }
  
  .btn-go {
    font-size: 11px;
    padding: 6px 12px;
  }
  
  .grid-info {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }
  
  .info-tile {
    font-size: 13px;
  }
}

/* 小屏手机 */
@media (max-width: 479px) {
  #app {
    padding: 6px 10px;
    height: 100%;
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
  }
  
  .left-side {
    grid-template-rows: 300px auto;
  }
  
  .right-side {
    max-height: 350px;
  }
  
  .title-group h1 {
    font-size: 14px;
  }
  
  .title-group p {
    font-size: 10px;
  }
  
  .route-planner {
    width: 150px;
    padding: 8px;
  }
  
  .route-input {
    font-size: 10px;
    padding: 4px 6px;
    margin-bottom: 4px;
  }
  
  .btn-go {
    font-size: 10px;
    padding: 5px 10px;
  }
  
  .grid-info {
    grid-template-columns: 1fr 1fr;
    gap: 6px;
  }
  
  .info-tile {
    font-size: 12px;
    padding: 8px;
  }
  
  .info-tile label {
    font-size: 9px;
  }
  
  .info-tile span {
    font-size: 13px;
  }
  
  .warning-content {
    padding: 20px;
    max-width: 90%;
  }
  
  .warning-text h3 {
    font-size: 20px;
  }
}

/* 移动端横屏适配 */
@media (orientation: landscape) and (max-width: 1024px) {
  #app {
    padding: 8px 16px;
    height: 100%;
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr 280px;
    grid-template-rows: 1fr;
    gap: 10px;
  }
  
  .left-side {
    grid-template-rows: 1fr 100px;
    gap: 10px;
  }
  
  .right-side {
    max-height: none;
    height: 100%;
    gap: 8px;
  }
  
  .title-group h1 {
    font-size: 16px;
  }
  
  .title-group p {
    font-size: 11px;
  }
  
  .route-planner {
    width: 160px;
    padding: 8px;
  }
  
  .route-input {
    font-size: 11px;
    padding: 5px 8px;
    margin-bottom: 4px;
  }
  
  .btn-go {
    font-size: 11px;
    padding: 6px 12px;
  }
  
  .grid-info {
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
  }
  
  .info-tile {
    font-size: 11px;
    padding: 6px;
  }
  
  .info-tile label {
    font-size: 9px;
  }
  
  .info-tile span {
    font-size: 12px;
  }
  
  .card {
    padding: 10px;
  }
  
  .lock-button-container {
    min-height: 40px;
  }
  
  .btn-action {
    padding: 8px;
    font-size: 13px;
  }
  
  .nav-item {
    padding: 6px 16px;
    font-size: 12px;
  }
}

/* 极小尺寸横屏设备适配 */
@media (orientation: landscape) and (max-width: 600px) {
  #app {
    padding: 6px 10px;
    height: 100%;
  }
  
  .dashboard-grid {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
    gap: 8px;
  }
  
  .left-side {
    grid-template-rows: 200px 100px;
    gap: 8px;
  }
  
  .right-side {
    max-height: 250px;
    height: 100%;
    gap: 6px;
  }
  
  .title-group h1 {
    font-size: 14px;
  }
  
  .title-group p {
    font-size: 10px;
  }
  
  .route-planner {
    width: 140px;
    padding: 6px;
  }
  
  .route-input {
    font-size: 10px;
    padding: 4px 6px;
    margin-bottom: 3px;
  }
  
  .btn-go {
    font-size: 10px;
    padding: 5px 10px;
  }
  
  .grid-info {
    grid-template-columns: repeat(2, 1fr);
    gap: 4px;
  }
  
  .info-tile {
    font-size: 10px;
    padding: 4px;
  }
  
  .info-tile label {
    font-size: 8px;
  }
  
  .info-tile span {
    font-size: 11px;
  }
  
  .card {
    padding: 8px;
  }
  
  .lock-button-container {
    min-height: 35px;
  }
  
  .btn-action {
    padding: 6px;
    font-size: 12px;
  }
  
  .nav-item {
    padding: 4px 12px;
    font-size: 11px;
  }
}

/* 小高度设备 */
@media (max-height: 600px) {
  .left-side {
    grid-template-rows: 280px auto;
  }
  
  .right-side {
    max-height: 300px;
  }
}

/* 极小高度设备 */
@media (max-height: 500px) {
  .left-side {
    grid-template-rows: 240px auto;
  }
  
  .right-side {
    max-height: 250px;
  }
  
  .route-planner {
    padding: 6px;
  }
  
  .route-input {
    font-size: 10px;
    padding: 3px 5px;
  }
  
  .btn-go {
    font-size: 10px;
    padding: 4px 8px;
  }
}

.geofence-warning {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.warning-content {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border: 2px solid #ff2a2a;
  border-radius: 16px;
  padding: 30px;
  max-width: 400px;
  text-align: center;
  box-shadow: 0 0 30px rgba(255, 42, 42, 0.5);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.warning-icon {
  font-size: 64px;
  margin-bottom: 20px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.warning-text h3 {
  margin: 0 0 10px;
  color: #ff2a2a;
  font-size: 24px;
  font-weight: bold;
}

.warning-text p {
  margin: 0;
  color: #eafcff;
  font-size: 14px;
  line-height: 1.6;
}

.warning-close {
  margin-top: 20px;
  padding: 12px 30px;
  background: #ff2a2a;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  transition: 0.3s;
}

.warning-close:hover {
  background: #ff4d4d;
  transform: scale(1.05);
  box-shadow: 0 0 20px rgba(255, 42, 42, 0.5);
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.header { display: flex; justify-content: space-between; align-items: center; padding-bottom: 12px; border-bottom: 1px solid rgba(0,234,255,0.1); margin-bottom: 10px; }
.title-group h1 { margin: 0; font-size: 18px; color: var(--accent); letter-spacing: 1px; text-transform: uppercase; }
.title-group p { margin: 2px 0 0; font-size: 11px; color: var(--text-dim); }

.style-switcher { display: flex; align-items: center; gap: 10px; background: rgba(0,0,0,0.25); padding: 6px 14px; border-radius: 20px; border: 1px solid var(--border); }
.style-dot { width: 14px; height: 14px; border-radius: 50%; cursor: pointer; border: 2px solid transparent; transition: 0.3s; }
.style-dot.active { border-color: #fff; box-shadow: 0 0 10px #fff; }

.page-container { flex: 1; display: flex; flex-direction: column; min-height: 0; overflow: hidden; }
.dashboard-grid { display: grid; grid-template-columns: 1fr 380px; gap: 14px; flex: 1; min-height: 0; overflow: hidden; }
.left-side { display: grid; grid-template-rows: 1fr 140px; gap: 14px; min-height: 0; }
.right-side { display: flex; flex-direction: column; gap: 12px; overflow-y: auto; padding-right: 4px; height: 100%; }
.right-side::-webkit-scrollbar { width: 6px; }

/* 状态面板响应式样式 */
.status-panel {
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

.status-center {
  text-align: center;
}

.status-right {
  text-align: right;
}

@media (max-width: 900px) {
  .status-panel {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
    padding: 15px !important;
  }
  
  .status-center {
    text-align: center;
    display: flex;
    flex-direction: column;
    gap: 8px;
    padding-top: 12px;
    border-top: 1px solid rgba(255,255,255,0.05);
  }

  .status-center .btn-outline {
    align-self: center;
    width: auto;
    min-width: 100px;
  }

  .status-right {
    text-align: left;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 12px;
    border-top: 1px solid rgba(255,255,255,0.05);
  }
}

::-webkit-scrollbar { width: 6px; }
.right-side::-webkit-scrollbar-track { background: rgba(0, 0, 0, 0.1); border-radius: 3px; }
.right-side::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 3px; }
.right-side::-webkit-scrollbar-thumb:hover { background: var(--accent-glow); }

.card { background: var(--bg-panel); border: 1px solid var(--border); border-radius: 12px; backdrop-filter: blur(10px); position: relative; overflow: hidden; }

#map-container { width: 100%; height: 100%; border-radius: 10px; }
.map-tools { position: absolute; top: 15px; right: 15px; display: flex; flex-direction: column; gap: 8px; z-index: 10; }
.tool-btn { background: rgba(5, 18, 26, 0.85); border: 1px solid var(--accent); color: var(--accent); padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 11px; font-weight: bold; }
.tool-btn.active { background: var(--accent); color: #000; }

.route-planner {
  position: absolute; top: 15px; left: 15px; z-index: 10;
  background: rgba(5, 18, 26, 0.9); border: 1px solid var(--border);
  padding: 10px; border-radius: 8px; width: 260px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.5);
}
.route-input {
  width: 100%; background: rgba(255,255,255,0.05); border: 1px solid var(--border);
  color: #fff; padding: 6px 10px; margin-bottom: 6px; border-radius: 4px; font-size: 12px;
}
.route-input:focus { outline: none; border-color: var(--accent); background: rgba(0, 234, 255, 0.1); }

input[type="range"] {
  -webkit-appearance: none;
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: rgba(255, 255, 255, 0.1);
  outline: none;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--accent);
  cursor: pointer;
  box-shadow: 0 0 10px var(--accent);
  transition: 0.2s;
}

input[type="range"]::-webkit-slider-thumb:hover {
  transform: scale(1.2);
  box-shadow: 0 0 15px var(--accent);
}

input[type="range"]::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--accent);
  cursor: pointer;
  border: none;
  box-shadow: 0 0 10px var(--accent);
  transition: 0.2s;
}

input[type="range"]::-moz-range-thumb:hover {
  transform: scale(1.2);
  box-shadow: 0 0 15px var(--accent);
}

.btn-go { background: var(--accent); color: #000; border: none; width: 100%; padding: 6px; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 12px; }

.panel { padding: 16px; display: flex; flex-direction: column; }
.panel-hd { font-size: 13px; font-weight: bold; margin-bottom: 12px; color: var(--text-dim); display: flex; justify-content: space-between; border-left: 3px solid var(--accent); padding-left: 8px; }

.gauge-wrap { position: relative; width: 100px; height: 100px; margin: 0 auto; flex-shrink: 0; }
.gauge-text { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
.gauge-text .big { font-size: 28px; font-weight: 800; color: var(--accent); }
.gauge-text .sml { font-size: 10px; opacity: 0.6; }

.grid-info { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.info-tile { background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.04); }
.info-tile label { font-size: 10px; color: var(--text-dim); display: block; margin-bottom: 4px; }
.info-tile span { font-size: 15px; font-weight: bold; color: var(--accent); }

.progress-container { margin-top: 10px; }
.bar-bg { height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; margin-top: 6px; }
.bar-fill { height: 100%; background: var(--accent); box-shadow: 0 0 10px var(--accent); transition: 1s ease; }

.sub-page { flex: 1; background: var(--bg-panel); border: 1px solid var(--border); border-radius: 12px; padding: 20px; overflow-y: auto; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-content: start; }
.full-width { grid-column: 1 / -1; }

.detail-item { display: flex; justify-content: space-between; padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }
.detail-item:last-child { border-bottom: none; }
.detail-value { font-family: monospace; color: var(--accent); }

.user-card { display: flex; align-items: center; gap: 20px; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 10px; margin-bottom: 20px; }
.avatar { width: 80px; height: 80px; border-radius: 50%; background: var(--border); display: flex; align-items: center; justify-content: center; font-size: 30px; border: 2px solid var(--accent); box-shadow: 0 0 15px var(--accent-glow); }

.bottom-nav { height: 55px; display: flex; gap: 12px; align-items: center; margin-top: 12px; }
.nav-item { padding: 8px 20px; border-radius: 8px; background: rgba(0, 234, 255, 0.05); border: 1px solid rgba(0, 234, 255, 0.15); color: #fff; cursor: pointer; font-size: 13px; transition: 0.3s; flex: 1; text-align: center; }
.nav-item:hover { background: rgba(0, 234, 255, 0.15); }
.nav-item.active { background: var(--accent); color: #000; font-weight: bold; box-shadow: 0 0 15px var(--accent-glow); }

.btn-action { background: var(--accent); color: #001a1d; border: none; padding: 10px; border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: 10px; width: 100%; }
.btn-outline { background: transparent; border: 1px solid var(--accent); color: var(--accent); padding: 4px 10px; border-radius: 4px; cursor: pointer; font-size: 11px; }

.lock-button-container {
  margin-top: auto;
  padding-top: 10px;
  min-height: 50px;
}

.fab-group { position: fixed; bottom: 85px; right: 30px; display: flex; flex-direction: column; gap: 12px; z-index: 100; }
.fab { width: 48px; height: 48px; border-radius: 50%; background: var(--bg-panel); border: 1px solid var(--accent); display: flex; align-items: center; justify-content: center; color: var(--accent); cursor: pointer; box-shadow: 0 0 15px var(--accent-glow); transition: 0.3s; backdrop-filter: blur(5px); }
.fab:hover { background: var(--accent); color: #000; transform: scale(1.05); }
.fab.large { width: 58px; height: 58px; font-size: 24px; }

/* 移动端适配fab-group */
@media (max-width: 767px) {
  .fab-group {
    position: fixed;
    bottom: 20px;
    right: 50%;
    transform: translateX(50%);
    flex-direction: row;
    gap: 20px;
    background: rgba(7, 35, 50, 0.9);
    padding: 10px 20px;
    border-radius: 40px;
    border: 1px solid var(--border);
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    width: auto;
  }
  
  .fab {
    width: 44px;
    height: 44px;
    font-size: 18px;
    box-shadow: none;
    background: transparent;
    border: 1px solid rgba(0, 234, 255, 0.3);
  }
  
  .fab:hover {
    transform: scale(1.1);
  }
  
  .fab.large {
    width: 54px;
    height: 54px;
    font-size: 24px;
    background: var(--accent);
    color: #000;
    border: none;
    margin-top: -20px;
    box-shadow: 0 0 15px var(--accent-glow);
  }
}

@media (max-width: 479px) {
  .fab-group {
    bottom: 15px;
    gap: 15px;
    padding: 8px 16px;
  }
  
  .fab {
    width: 38px;
    height: 38px;
    font-size: 16px;
  }
  
  .fab.large {
    width: 48px;
    height: 48px;
    font-size: 20px;
    margin-top: -15px;
  }
}

/* 针对横屏模式的特殊处理 */
@media (orientation: landscape) and (max-height: 500px) {
  .fab-group {
    right: 20px;
    bottom: 50%;
    transform: translateY(50%);
    flex-direction: column;
    background: rgba(7, 35, 50, 0.8);
    padding: 10px;
    border-radius: 30px;
    width: auto;
    gap: 10px;
  }

  .fab.large {
    margin-top: 0;
  }
}

/* 竖屏模式强制滚动支持 */
@media (max-width: 767px) {
  body, html {
    overflow-y: auto !important;
    height: auto !important;
  }
  
  #app {
    height: auto !important;
    min-height: 100vh;
    overflow: visible !important;
    padding-bottom: 80px; /* 为底部FAB留出空间 */
  }
  
  .page-container {
    height: auto !important;
    overflow: visible !important;
    display: block !important;
  }
  
  .dashboard-grid {
    display: flex !important;
    flex-direction: column;
    height: auto !important;
    overflow: visible !important;
  }
  
  .left-side, .right-side {
    height: auto !important;
    max-height: none !important;
    overflow: visible !important;
  }
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
</style>
