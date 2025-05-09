<template>
  <v-container fluid>
    <v-row>
      <!-- Left Sidebar -->
      <v-col cols="12" md="2" class="sidebar">
        <h3 class="text-h5 font-weight-medium">Jan’25</h3>
        <h4 class="text-h6 font-weight-bold">Software Engg.</h4>

        <v-select
            v-model="selectedWeek"
            :items="weeks"
            label="Week Selection"
            dense
            outlined
            class="mt-4"
        ></v-select>

        <v-card class="key-stats mt-4" outlined>
          <v-card-title class="text-h6">Key Stats</v-card-title>
          <v-card-text>
            <p><strong>{{ keyStats.weeklyUsers }}</strong> Weekly Users</p>
            <p><strong>{{ keyStats.doubtQueries }}</strong> Doubt Queries</p>
            <p><strong>{{ keyStats.solvesBookmarked }}</strong> Solves Bookmarked</p>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Main Dashboard Content -->
      <v-col cols="12" md="7">
        <h2 class="text-h5 font-weight-medium">Hello Admin,</h2>

        <!-- Weekly Performance Chart -->
        <v-card class="chart-card mt-4" outlined>
          <v-card-title>Weekly Performance</v-card-title>
          <v-card-text>
            <canvas ref="barChartCanvas"></canvas>
          </v-card-text>
        </v-card>

        <v-row>
          <!-- GenAI Tool Perception Chart -->
          <v-col cols="6">
            <v-card class="chart-card mt-4" outlined>
              <v-card-title>GenAI Tool Perception</v-card-title>
              <v-card-text>
                <canvas ref="lineChartCanvas"></canvas>
              </v-card-text>
            </v-card>
          </v-col>

          <!-- Key Issues Faced -->
          <v-col cols="6">
            <v-card class="chart-card mt-4" outlined>
              <v-card-title class="d-flex justify-space-between align-center">
                Key Issues Faced
                <v-chip class="week-chip">{{ selectedWeek }}</v-chip>
              </v-card-title>
              <v-card-text>
                <ul class="issues-list">
                  <li v-for="(issue, index) in keyIssues" :key="index">{{ index + 1 }}. {{ issue }}</li>
                </ul>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-col>

      <!-- Upload Console -->
      <v-col cols="12" md="3">
        <v-card class="upload-console" outlined>
          <v-card-title class="d-flex justify-space-between align-center">
            Upload Console
            <v-chip class="week-chip">{{ selectedWeek }}</v-chip>
          </v-card-title>
          <v-card-text>
            <v-file-input label="Attach Video Link..." outlined dense></v-file-input>
            <v-btn block color="primary" class="mt-2">Upload</v-btn>

            <v-file-input label="Upload PDF..." outlined dense class="mt-4"></v-file-input>
            <v-btn block color="primary" class="mt-2">Upload</v-btn>

            <v-file-input label="Upload Google Doc..." outlined dense class="mt-4"></v-file-input>
            <v-btn block color="primary" class="mt-2">Upload</v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Chart from 'chart.js/auto';

const selectedWeek = ref('Week 1');
const weeks = ref(['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8']);

const keyStats = ref({
  weeklyUsers: 'XX',
  doubtQueries: 'XX',
  solvesBookmarked: 'XX',
});

const keyIssues = ref(['Issue A', 'Issue B', 'Issue C', 'Issue D', 'Issue E']);

const barChartCanvas = ref(null);
const lineChartCanvas = ref(null);

const initCharts = () => {
  if (barChartCanvas.value) {
    new Chart(barChartCanvas.value.getContext('2d'), {
      type: 'bar',
      data: {
        labels: ['Wk 1', 'Wk 2', 'Wk 3', 'Wk 4', 'Wk 5', 'Wk 6', 'Wk 7', 'Wk 8', 'Wk 9', 'Wk 10'],
        datasets: [
          {
            label: 'Avg Score',
            data: [60, 70, 75, 50, 80, 85, 78, 90, 45, 88],
            backgroundColor: (ctx) => ctx.dataIndex === 3 || ctx.dataIndex === 8 ? '#E57373' : '#42A5F5',
          },
        ],
      },
    });
  }

  if (lineChartCanvas.value) {
    new Chart(lineChartCanvas.value.getContext('2d'), {
      type: 'line',
      data: {
        labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
        datasets: [
          {
            label: 'Perception',
            data: [20, 40, 30, 50, 60],
            borderColor: '#66BB6A',
            fill: false,
          },
        ],
      },
    });
  }
};

onMounted(() => {
  initCharts();
});
</script>

<style scoped>
.sidebar {
  padding: 20px;
  background: #F5F5F5;
  border-right: 2px solid #E0E0E0;
}

.key-stats {
  padding: 15px;
  background: #FFFFFF;
}

.chart-card {
  padding: 15px;
  border-radius: 10px;
}

.week-chip {
  background: #757575;
  color: white;
}

.upload-console {
  padding: 15px;
  border-radius: 10px;
}

.issues-list {
  list-style-type: none;
  padding: 0;
  font-size: 16px;
}

.issues-list li {
  margin-bottom: 5px;
}
</style>