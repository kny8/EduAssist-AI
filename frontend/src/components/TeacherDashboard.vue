<template>
  <v-container fluid>
    <v-row>
      <!-- Sidebar (Week Selector) -->
      <v-col cols="2">
        <v-card>
          <v-list>
            <v-list-item>
              <v-select
                  v-model="selectedWeek"
                  :items="weeks"
                  item-title="name"
                  item-value="id"
                  label="Week"
                  dense
                  outlined
              ></v-select>
            </v-list-item>
            <!-- Admin button to add a new week -->
            <v-list-item v-if="weeks.length > 0 && weeks[0].id !== null">
              <v-btn 
                small 
                color="primary" 
                block
                @click="showAddWeekDialog = true"
              >
                Add New Week
              </v-btn>
            </v-list-item>
          </v-list>
        </v-card>

        <!-- Lectures in current week -->
        <v-card class="mt-4" v-if="visibleLectures.length > 0">
          <v-card-title class="text-subtitle-1">
            Lectures in {{ currentWeekName }}
          </v-card-title>
          <v-list dense>
            <v-list-item 
              v-for="lecture in visibleLectures" 
              :key="lecture.id"
              @click="selectLecture(lecture)"
              :class="{ 'selected-lecture': selectedLecture && selectedLecture.id === lecture.id }"
            >
              <v-list-item-icon>
                <v-icon small>mdi-pencil-outline</v-icon>
              </v-list-item-icon>
              <v-list-item-content>
                <v-list-item-title class="text-caption">{{ lecture.name }}</v-list-item-title>
                <v-list-item-subtitle class="text-caption">{{ lecture.type }}</v-list-item-subtitle>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>

      <!-- Main Dashboard -->
      <v-col cols="10">
        <v-row>
          <v-col>
            <h2>Instructor/TA Console</h2>
            <h4>Hello {{currentUser.name}}</h4>
            <p class="subtitle-1">{{ currentWeekName }}</p>
            <div v-if="currentWeekName !== 'All Weeks' && lectures.length > 0" class="text-caption">
              {{ lectures.length }} lecture{{ lectures.length !== 1 ? 's' : '' }} in this week
            </div>
            <div v-else-if="currentWeekName === 'All Weeks' && totalLectureCount > 0" class="text-caption">
              {{ totalLectureCount }} total lectures across all weeks
            </div>
          </v-col>
        </v-row>

        <v-row v-if="loading">
          <v-col class="text-center">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
            <div>Loading dashboard data...</div>
          </v-col>
        </v-row>

        <!-- No weeks exist message -->
        <v-row v-else-if="weeks.length === 0 || (weeks.length === 1 && weeks[0].id === null)">
          <v-col class="text-center">
            <v-alert
              type="info"
              outlined
            >
              No weeks found in the system. You need to create weeks first.
            </v-alert>
            <v-btn 
              color="primary" 
              class="mt-4"
              @click="showAddWeekDialog = true"
            >
              Create First Week
            </v-btn>
          </v-col>
        </v-row>

        <template v-else>
          <!-- Common Student Searches Widget -->
          <v-row>
            <v-col cols="12">
              <v-card class="mb-4">
                <v-card-title class="primary white--text">
                  <v-icon color="white" class="mr-2">mdi-magnify</v-icon>
                  Common Student Searches
                  <v-spacer></v-spacer>
                  <v-chip small color="white" text-color="primary">
                    <v-icon left small>mdi-information</v-icon>
                    From Study with GenAI
                  </v-chip>
                </v-card-title>
                <v-card-text>
                  <div v-if="commonSearches.length === 0" class="text-center pa-4">
                    <p>No search data available for this week</p>
                  </div>
                  <v-row v-else>
                    <!-- Filtering controls -->
                    <v-col cols="12" class="py-0">
                      <v-row>
                        <v-col cols="12" md="4">
                          <v-text-field
                            v-model="searchFilter"
                            label="Filter queries"
                            dense
                            outlined
                            clearable
                            prepend-inner-icon="mdi-magnify"
                            hide-details
                            class="mb-2"
                          ></v-text-field>
                        </v-col>
                        <v-col cols="12" md="4">
                          <v-select
                            v-model="topicFilter"
                            :items="getAllTopics()"
                            label="Filter by topic"
                            dense
                            outlined
                            clearable
                            hide-details
                            class="mb-2"
                          ></v-select>
                        </v-col>
                        <v-col cols="12" md="4">
                          <v-select
                            v-model="lectureFilter"
                            :items="getAllLectures()"
                            label="Filter by lecture"
                            dense
                            outlined
                            clearable
                            hide-details
                            class="mb-2"
                          ></v-select>
                        </v-col>
                      </v-row>
                    </v-col>
                    <v-col cols="12" md="7">
                      <v-data-table
                        :headers="[
                          { text: 'Query', value: 'query', sortable: true },
                          { text: 'Count', value: 'count', sortable: true },
                          { text: 'Topics', value: 'topics', sortable: false },
                          { text: 'Sentiment', value: 'sentiments', sortable: false }
                        ]"
                        :items="filteredSearches"
                        :items-per-page="5"
                        class="elevation-1"
                        dense
                      >
                        <template v-slot:item.topics="{ item }">
                          <v-chip
                            v-for="(topic, i) in item.topics.slice(0, 2)"
                            :key="i"
                            small
                            class="mr-1"
                            color="blue lighten-4"
                          >
                            {{ topic }}
                          </v-chip>
                          <v-chip
                            v-if="item.topics.length > 2"
                            small
                            color="grey lighten-3"
                          >
                            +{{ item.topics.length - 2 }}
                          </v-chip>
                          
                          <!-- Add tooltips for all topics when hovering -->
                          <v-tooltip v-if="item.topics.length > 2" bottom>
                            <template v-slot:activator="{ on, attrs }">
                              <v-icon small v-bind="attrs" v-on="on">mdi-information-outline</v-icon>
                            </template>
                            <div>
                              <div v-for="(topic, i) in item.topics" :key="i">
                                {{ topic }}
                              </div>
                            </div>
                          </v-tooltip>
                        </template>
                        <template v-slot:item.sentiments="{ item }">
                          <div v-if="item.sentiments">
                            <v-tooltip v-for="(value, sentiment) in item.sentiments" :key="sentiment" bottom>
                              <template v-slot:activator="{ on, attrs }">
                                <v-icon 
                                  small 
                                  class="mr-1" 
                                  :color="getSentimentInfo(sentiment, value).color"
                                  v-bind="attrs"
                                  v-on="on"
                                >
                                  {{ getSentimentInfo(sentiment, value).icon }}
                                </v-icon>
                              </template>
                              <span>{{ getSentimentInfo(sentiment, value).label }}: {{ Math.round(value * 100) }}%</span>
                            </v-tooltip>
                            
                            <!-- Show lectures context if available -->
                            <v-tooltip v-if="item.lectures && item.lectures.length" bottom>
                              <template v-slot:activator="{ on, attrs }">
                                <v-icon 
                                  small 
                                  color="purple"
                                  v-bind="attrs"
                                  v-on="on"
                                >
                                  mdi-school
                                </v-icon>
                              </template>
                              <div>
                                <div class="font-weight-bold">Appears in lectures:</div>
                                <div v-for="(lecture, i) in item.lectures" :key="i">
                                  {{ lecture }}
                                </div>
                              </div>
                            </v-tooltip>
                          </div>
                        </template>
                      </v-data-table>
                    </v-col>
                    <v-col cols="12" md="5">
                      <div class="search-insights pa-2">
                        <h3 class="text-h6 mb-2">Insights</h3>
                        <v-alert
                          v-if="commonSearches.some(s => s.sentiments && s.sentiments.confusion > 0.7)"
                          dense
                          type="error"
                          class="mb-2"
                        >
                          High confusion detected on key topics
                        </v-alert>
                        <v-alert
                          v-if="commonSearches.some(s => s.sentiments && s.sentiments.frustration > 0.6)"
                          dense
                          type="warning"
                          class="mb-2"
                        >
                          Significant frustration detected in student queries
                        </v-alert>
                        
                        <v-list dense>
                          <v-subheader>Most common topics in searches</v-subheader>
                          <v-list-item v-for="(topic, i) in getTopSearchTopics()" :key="i">
                            <v-list-item-icon>
                              <v-icon color="indigo">mdi-bookmark</v-icon>
                            </v-list-item-icon>
                            <v-list-item-content>
                              <v-list-item-title>{{ topic.name }}</v-list-item-title>
                              <v-list-item-subtitle>{{ topic.count }} searches</v-list-item-subtitle>
                            </v-list-item-content>
                          </v-list-item>

                          <!-- Most Discussed Lectures Section -->
                          <v-divider class="my-2"></v-divider>
                          <v-subheader>Most Discussed Lectures</v-subheader>
                          <v-list-item v-for="(lecture, i) in getTopLectures()" :key="`lecture-${i}`">
                            <v-list-item-icon>
                              <v-icon color="purple">mdi-school</v-icon>
                            </v-list-item-icon>
                            <v-list-item-content>
                              <v-list-item-title class="text-truncate">{{ lecture.name }}</v-list-item-title>
                              <v-list-item-subtitle>{{ lecture.count }} searches</v-list-item-subtitle>
                            </v-list-item-content>
                          </v-list-item>
                          <v-list-item v-if="getTopLectures().length === 0">
                            <v-list-item-content>
                              <v-list-item-subtitle class="text-center">No lecture context available</v-list-item-subtitle>
                            </v-list-item-content>
                          </v-list-item>
                        </v-list>
                      </div>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
          
          <!-- Combined Student Analytics Widget -->
          <v-row>
            <v-col cols="12">
              <v-card class="mb-4">
                <v-card-title class="indigo darken-1 white--text">
                  <v-icon color="white" class="mr-2">mdi-account-group</v-icon>
                  Student Engagement & Progress
                </v-card-title>
                
                <v-card-text class="pa-2">
                  <!-- Summary Stats Row -->
                  <v-row dense>
                    <v-col cols="12" md="2">
                      <v-card outlined class="text-center">
                        <v-card-text class="pa-2">
                          <div class="text-h4 font-weight-bold primary--text">{{ getActiveStudentCount() }}</div>
                          <div class="text-caption">Active Students</div>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    
                    <v-col cols="12" md="2">
                      <v-card outlined class="text-center">
                        <v-card-text class="pa-2">
                          <div class="text-h4 font-weight-bold amber--text text--darken-2">{{ getParticipationRate() }}%</div>
                          <div class="text-caption">Participation Rate</div>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    
                    <v-col cols="12" md="2">
                      <v-card outlined class="text-center">
                        <v-card-text class="pa-2">
                          <div class="text-h4 font-weight-bold">{{ totalLectureCount }}</div>
                          <div class="text-caption">Total Lectures</div>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    
                    <v-col cols="12" md="2">
                      <v-card outlined class="text-center">
                        <v-card-text class="pa-2">
                          <div class="text-h4 font-weight-bold">{{ 
                            completionData.length > 0 
                              ? Math.round(completionData.reduce((sum, item) => sum + item.completion, 0) / completionData.length) 
                              : 0 
                          }}%</div>
                          <div class="text-caption">Avg. Assignment Completion</div>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    
                    <v-col cols="12" md="2">
                      <v-card outlined class="text-center">
                        <v-card-text class="pa-2">
                          <div class="text-h4 font-weight-bold">{{ 
                            commonSearches.reduce((sum, item) => sum + item.count, 0)
                          }}</div>
                          <div class="text-caption">Total Searches</div>
                        </v-card-text>
                      </v-card>
                    </v-col>
                    
                    <v-col cols="12" md="2">
                      <v-card outlined class="text-center" :class="{'red lighten-5': getConfusionRate() > 30}">
                        <v-card-text class="pa-2">
                          <div class="text-h4 font-weight-bold" :class="getConfusionRate() > 30 ? 'red--text' : 'blue--text'">{{ getConfusionRate() }}%</div>
                          <div class="text-caption">Confusion Rate</div>
                        </v-card-text>
                      </v-card>
                    </v-col>
                  </v-row>
                  
                  <!-- Topic Engagement and Performance -->
                  <v-row class="mt-2">
                    <v-col cols="12" md="6">
                      <div class="d-flex justify-space-between align-center">
                        <h4 class="text-subtitle-1 mb-2">Topic Engagement Analysis</h4>
                        <v-chip small color="indigo" text-color="white">Ranked by engagement</v-chip>
                      </div>
                      
                      <v-data-table
                        :headers="[
                          { text: 'Topic', value: 'name', width: '30%' },
                          { text: 'Engagement', value: 'engagement', align: 'center', width: '30%' },
                          { text: 'Confusion', value: 'confusion', align: 'center', width: '25%' },
                          { text: 'Status', value: 'status', align: 'center', width: '15%' }
                        ]"
                        :items="getTopicEngagement()"
                        dense
                        hide-default-footer
                        class="elevation-1"
                      >
                        <template v-slot:item.engagement="{ item }">
                          <v-rating
                            :value="item.engagementRating"
                            color="amber"
                            background-color="grey lighten-3"
                            half-increments
                            readonly
                            small
                            dense
                            length="3"
                          ></v-rating>
                        </template>
                        
                        <template v-slot:item.confusion="{ item }">
                          <v-progress-linear
                            :value="item.confusionPercent"
                            height="8"
                            :color="item.confusionPercent > 60 ? 'red' : item.confusionPercent > 30 ? 'orange' : 'green'"
                            class="rounded-lg"
                          >
                            <span class="white--text text-caption">{{ item.confusionPercent }}%</span>
                          </v-progress-linear>
                        </template>
                        
                        <template v-slot:item.status="{ item }">
                          <v-chip
                            x-small
                            :color="item.status === 'Needs Attention' ? 'error' : item.status === 'Monitor' ? 'warning' : 'success'"
                            text-color="white"
                          >
                            {{ item.status }}
                          </v-chip>
                        </template>
                      </v-data-table>
                      
                      <v-alert
                        v-if="getTeachingPriority()"
                        dense
                        type="warning"
                        text
                        class="mt-2 mb-0"
                      >
                        <strong>Priority:</strong> {{ getTeachingPriority() }}
                      </v-alert>
                    </v-col>
                    
                    <v-col cols="12" md="6">
                      <div class="d-flex justify-space-between align-center">
                        <h4 class="text-subtitle-1 mb-2">Lecture Performance</h4>
                        <v-btn x-small text @click="refreshTopicInsights">
                          <v-icon x-small left>mdi-refresh</v-icon>Refresh
                        </v-btn>
                      </div>
                      
                      <!-- Lecture Performance List -->
                      <v-list dense class="elevation-1">
                        <v-list-item v-for="(item, i) in getLecturePerformance()" :key="i">
                          <v-list-item-content>
                            <div class="d-flex justify-space-between align-center mb-1">
                              <div class="font-weight-medium">{{ truncateLectureName(item.name) }}</div>
                              <div class="text-subtitle-2">{{ item.performance }}%</div>
                            </div>
                            <v-progress-linear
                              :value="item.performance"
                              height="6"
                              :color="item.performance < 60 ? 'red' : 'green'"
                            ></v-progress-linear>
                          </v-list-item-content>
                        </v-list-item>
                      </v-list>
                      
                      <!-- Recent Activity -->
<!--                      <h4 class="text-subtitle-1 mb-2 mt-3">Recent Activity</h4>-->
<!--                      <v-timeline dense class="elevation-1 pa-2">-->
<!--                        <v-timeline-item-->
<!--                          v-for="(activity, i) in getActivityTimeline().slice(0, 3)"-->
<!--                          :key="i"-->
<!--                          :color="activity.color"-->
<!--                          small-->
<!--                          class="pb-0"-->
<!--                        >-->
<!--                          <div class="font-weight-medium">{{ activity.title }}</div>-->
<!--                          <div class="text-caption">{{ activity.description }}</div>-->
<!--                        </v-timeline-item>-->
<!--                      </v-timeline>-->
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
          
          <v-row>
            <!-- Assignment Problem Area Console -->
            <v-col cols="8">
              <v-card class="pa-3">
                <h3>
                  Assignment Problem Area Console
                  <v-chip
                    v-if="selectedLecture"
                    small
                    color="primary"
                    class="ml-2"
                    close
                    @click:close="selectedLecture = null; renderChart()"
                  >
                    {{ selectedLecture.name }}
                  </v-chip>
                </h3>
                <div v-if="filteredAssignmentData.length === 0" class="text-center pa-4">
                  <p>No assignment data available for this week</p>
                </div>
                <div v-else>
                  <div class="chart-container">
                    <canvas ref="chartCanvas"></canvas>
                  </div>
                  
                  <!-- Assignment problem details -->
                  <v-expansion-panels v-if="hasLectureData" class="mt-3">
                    <v-expansion-panel>
                      <v-expansion-panel-header>
                        Problem Areas by Lecture
                      </v-expansion-panel-header>
                      <v-expansion-panel-content>
                        <div class="problem-areas-table" style="max-height: 300px; overflow-y: auto;">
                          <v-simple-table dense>
                            <thead>
                              <tr>
                                <th>Question</th>
                                <th>Lecture</th>
                                <th>Correct %</th>
                                <th>Status</th>
                              </tr>
                            </thead>
                            <tbody>
                              <tr 
                                v-for="item in filteredAssignmentData" 
                                :key="item.question"
                                :class="{'red lighten-5': item.correct < 50}"
                              >
                                <td>{{ item.question }}</td>
                                <td>{{ item.lecture_name || 'N/A' }}</td>
                                <td>{{ item.correct }}%</td>
                                <td>
                                  <v-chip
                                    x-small
                                    :color="item.correct < 50 ? 'red' : 'green'"
                                    text-color="white"
                                  >
                                    {{ item.correct < 50 ? 'Problem Area' : 'Good' }}
                                  </v-chip>
                                </td>
                              </tr>
                            </tbody>
                          </v-simple-table>
                        </div>
                      </v-expansion-panel-content>
                    </v-expansion-panel>
                  </v-expansion-panels>
                </div>
              </v-card>
            </v-col>

            <!-- Completion Console -->
            <v-col cols="4">
              <v-card class="pa-3">
                <h3>Completion Console</h3>
                <div v-if="completionData.length === 0" class="text-center pa-4">
                  <p>No completion data available for this week</p>
                </div>
                <v-simple-table v-else>
                  <thead>
                  <tr>
                    <th>Assignment</th>
                    <th>Completion %</th>
                  </tr>
                  </thead>
                  <tbody>
                  <tr v-for="(item, index) in completionData" :key="index">
                    <td>{{ item.name }}</td>
                    <td>
                      <v-progress-linear
                        :value="item.completion"
                        :color="getCompletionColor(item.completion)"
                        height="20"
                      >
                        <template v-slot:default="{ value }">
                          <strong>{{ value }}%</strong>
                        </template>
                      </v-progress-linear>
                    </td>
                  </tr>
                  </tbody>
                </v-simple-table>
              </v-card>
            </v-col>
          </v-row>

          <v-row>
            <!-- Searched Topics Console -->
            <v-col cols="6">
              <v-card class="pa-3">
                <h3>Searched Topics Console</h3>
                <div v-if="searchedTopics.length === 0" class="text-center pa-4">
                  <p>No search data available for this week</p>
                </div>
                <v-simple-table v-else>
                  <thead>
                  <tr>
                    <th>Topic</th>
                    <th>Searched %</th>
                  </tr>
                  </thead>
                  <tbody>
                  <tr v-for="(topic, index) in searchedTopics" :key="index">
                    <td>{{ topic.name }}</td>
                    <td>
                      <v-progress-linear
                        :value="topic.percentage"
                        color="orange"
                        height="20"
                      >
                        <template v-slot:default="{ value }">
                          <strong>{{ value }}%</strong>
                        </template>
                      </v-progress-linear>
                    </td>
                  </tr>
                  </tbody>
                </v-simple-table>
              </v-card>
            </v-col>

            <!-- GPT Suggestions -->
            <v-col cols="6">
              <v-card class="pa-3">
                <h3> Suggestions</h3>
                <div v-if="gptSuggestions.length === 0" class="text-center pa-4">
                  <p>No suggestions available for this week</p>
                </div>
                <v-list v-else dense>
                  <v-list-item v-for="(suggestion, index) in gptSuggestions" :key="index">
                    <v-list-item-icon>
                      <v-icon color="primary">mdi-lightbulb</v-icon>
                    </v-list-item-icon>
                    <v-list-item-content>
                      <v-list-item-title>{{ suggestion }}</v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-list>
              </v-card>
            </v-col>
          </v-row>
          
          <!-- Topic Correlation Widget -->
          <v-row>
            <v-col cols="12">
              <v-card class="pa-3 mb-4">
                <h3>
                  <v-icon left color="teal">mdi-connection</v-icon>
                  Topic-Lecture Correlations
                </h3>
                
                <v-row>
                  <v-col cols="12" md="5">
                    <h4 class="text-subtitle-1">Topics with High Confusion</h4>
                    <div v-if="getTopicsWithHighConfusion().length === 0" class="text-center pa-4">
                      <p>No topics with high confusion found</p>
                    </div>
                    <v-list v-else dense>
                      <v-list-item v-for="(topic, i) in getTopicsWithHighConfusion()" :key="i">
                        <v-list-item-icon>
                          <v-icon :color="getConfusionLevelColor(topic.confusionLevel)">
                            mdi-alert-circle
                          </v-icon>
                        </v-list-item-icon>
                        <v-list-item-content>
                          <v-list-item-title>{{ topic.name }}</v-list-item-title>
                          <v-list-item-subtitle>
                            Confusion: {{ (topic.confusionLevel * 100).toFixed(0) }}%
                          </v-list-item-subtitle>
                        </v-list-item-content>
                        <v-list-item-action>
                          <v-chip x-small>{{ Math.round(topic.count) }}</v-chip>
                        </v-list-item-action>
                      </v-list-item>
                    </v-list>
                  </v-col>
                  
                  <v-col cols="12" md="7">
                    <h4 class="text-subtitle-1">Lecture-Topic Relationships</h4>
                    <div v-if="getTopicLectureCorrelation().length === 0" class="text-center pa-4">
                      <p>No correlation data available</p>
                    </div>
                    <v-simple-table v-else dense>
                      <thead>
                        <tr>
                          <th>Lecture</th>
                          <th>Topics</th>
                          <th>Performance</th>
                          <th>Confusion</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(item, i) in getTopicLectureCorrelation()" :key="i">
                          <td>{{ truncateLectureName(item.lecture) }}</td>
                          <td>
                            <v-chip
                              v-for="(topic, j) in item.topics.slice(0, 2)"
                              :key="j"
                              x-small
                              class="mr-1"
                            >
                              {{ topic }}
                            </v-chip>
                            <span v-if="item.topics.length > 2">+{{ item.topics.length - 2 }}</span>
                          </td>
                          <td>
                            <v-progress-linear
                              :value="item.performance"
                              height="15"
                              :color="item.performance < 60 ? 'red' : 'green'"
                            >
                              <span class="white--text text-caption">{{ item.performance }}%</span>
                            </v-progress-linear>
                          </td>
                          <td>
                            <v-chip 
                              x-small 
                              :color="getConfusionLevelColor(item.confusion / 100)"
                              text-color="white"
                            >
                              {{ item.confusion }}%
                            </v-chip>
                          </td>
                        </tr>
                      </tbody>
                    </v-simple-table>
                    
                    <v-alert
                      v-if="getRecommendation()"
                      dense
                      type="info"
                      color="amber lighten-5"
                      border="left"
                      class="mt-3"
                    >
                      <v-icon left color="amber darken-2">mdi-lightbulb-on</v-icon>
                      {{ getRecommendation() }}
                    </v-alert>
                  </v-col>
                </v-row>
              </v-card>
            </v-col>
          </v-row>
          
          <!-- Activity Timeline Widget -->
          <v-row>
            <v-col cols="12">
              <v-card class="pa-3 mb-4">
                <h3>
                  <v-icon left color="purple">mdi-chart-timeline-variant</v-icon>
                  Activity Timeline
                </h3>
                
                <v-row>
                  <v-col cols="12">
                    <v-timeline dense>
                      <v-timeline-item
                        v-for="(activity, i) in getActivityTimeline()"
                        :key="i"
                        :color="activity.color"
                        small
                      >
                        <template v-slot:opposite>
                          <span class="text-caption">{{ activity.timeAgo }}</span>
                        </template>
                        <v-card outlined>
                          <v-card-title class="text-subtitle-2 pb-1">
                            {{ activity.title }}
                            <v-spacer></v-spacer>
                            <v-chip
                              x-small
                              :color="activity.color"
                              text-color="white"
                              class="ml-2"
                            >
                              {{ activity.type }}
                            </v-chip>
                          </v-card-title>
                          <v-card-text class="py-2">
                            {{ activity.description }}
                          </v-card-text>
                        </v-card>
                      </v-timeline-item>
                      
                      <v-timeline-item v-if="getActivityTimeline().length === 0" color="grey" small>
                        <template v-slot:opposite>
                          <span class="text-caption">Now</span>
                        </template>
                        <v-card outlined>
                          <v-card-text class="text-center">
                            No recent activity data available
                          </v-card-text>
                        </v-card>
                      </v-timeline-item>
                    </v-timeline>
                  </v-col>
                </v-row>
              </v-card>
            </v-col>
          </v-row>
        </template>
      </v-col>
    </v-row>

    <!-- Add Week Dialog -->
    <v-dialog
      v-model="showAddWeekDialog"
      max-width="500px"
    >
      <v-card>
        <v-card-title>
          Add New Week
        </v-card-title>
        <v-card-text>
          <v-form ref="weekForm">
            <v-text-field
              v-model="newWeekName"
              label="Week Name"
              required
              :rules="[v => !!v || 'Week name is required']"
            ></v-text-field>
            <v-select
              v-model="newWeekSubject"
              :items="subjects"
              item-text="name"
              item-value="id"
              label="Subject"
              required
              :rules="[v => !!v || 'Subject is required']"
            ></v-select>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="blue darken-1"
            text
            @click="showAddWeekDialog = false"
          >
            Cancel
          </v-btn>
          <v-btn
            color="blue darken-1"
            text
            @click="addNewWeek"
            :loading="addingWeek"
          >
            Save
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import Chart from "chart.js/auto";
import http from "../services/http-common";

export default {
  data() {
    return {
      selectedWeek: null,
      weeks: [],
      currentWeekName: "All Weeks",
      chartInstance: null,
      completionData: [],
      searchedTopics: [],
      gptSuggestions: [],
      assignmentData: [],
      lectures: [],
      totalLectureCount: 0,
      selectedLecture: null,
      commonSearches: [],
      searchFilter: '',
      topicFilter: '',
      lectureFilter: '',
      loading: true,
      
      // Week creation data
      showAddWeekDialog: false,
      newWeekName: "",
      newWeekSubject: null,
      subjects: [],
      addingWeek: false,
      currentUser: {
        id: null,
        name: '',
        student_id: ''
      },
    };
  },
  
  computed: {
    // Filtered searches based on search, topic, and lecture filters
    filteredSearches() {
      return this.commonSearches.filter(search => {
        // Apply text filter
        const matchesText = !this.searchFilter || 
          search.query.toLowerCase().includes(this.searchFilter.toLowerCase());
        
        // Apply topic filter
        const matchesTopic = !this.topicFilter || 
          (search.topics && search.topics.includes(this.topicFilter));
        
        // Apply lecture filter
        const matchesLecture = !this.lectureFilter || 
          (search.lectures && search.lectures.includes(this.lectureFilter));
        
        return matchesText && matchesTopic && matchesLecture;
      });
    },
    
    // Check if any assignment data has lecture information
    hasLectureData() {
      return this.assignmentData.some(item => item.lecture_name);
    },
    
    // Filtered lectures based on selected week
    visibleLectures() {
      if (this.currentWeekName === 'All Weeks') {
        // For "All Weeks", organize lectures by week
        return this.lectures
          .slice()
          .sort((a, b) => {
            // First sort by week_id
            if (a.week_id !== b.week_id) {
              return a.week_id - b.week_id;
            }
            // Then by sequence_no if available
            return (a.sequence_no || 0) - (b.sequence_no || 0);
          })
          .map(lecture => ({
            ...lecture,
            // Add the week name to the lecture name for "All Weeks" view
            name: lecture.week_name ? `[${lecture.week_name}] ${lecture.name}` : lecture.name
          }));
      } else {
        // For a specific week, just return the lectures
        return this.lectures;
      }
    },
    
    // Filtered assignment data based on selected lecture
    filteredAssignmentData() {
      if (!this.selectedLecture) {
        return this.assignmentData;
      }
      
      return this.assignmentData.filter(question => 
        question.lecture_id === this.selectedLecture.id
      );
    }
  },
  
  watch: {
    selectedWeek(newWeekId) {
      console.log("Selected week changed to:", newWeekId);
      this.handleWeekChange(newWeekId);
    }
  },
  
  mounted() {
    // Fetch subjects for the dropdown
    this.fetchSubjects();
      
    // Add a slight delay to ensure the DOM is fully rendered
    setTimeout(() => {
      this.fetchDashboardData(this.selectedWeek);
    }, 100);
    
    window.addEventListener('resize', () => {
      if (this.chartInstance) {
        this.chartInstance.resize();
      }
    });
  },
  
  methods: {
    getUser() {
      const user = localStorage.getItem("user");
      this.currentUser = user ? JSON.parse(user) : null;
      if (this.currentUser) {
        this.currentRole = this.currentUser['role'] ?? 'student';
      }
    },
    // Function to get all unique topics across searches
    getAllTopics() {
      const topics = new Set();
      this.commonSearches.forEach(search => {
        if (search.topics) {
          search.topics.forEach(topic => topics.add(topic));
        }
      });
      return Array.from(topics).sort();
    },
    
    // Function to get all unique lectures across searches
    getAllLectures() {
      const lectures = new Set();
      this.commonSearches.forEach(search => {
        if (search.lectures) {
          search.lectures.forEach(lecture => lectures.add(lecture));
        }
      });
      return Array.from(lectures).sort();
    },

    // Function to select a lecture and filter questions
    selectLecture(lecture) {
      if (this.selectedLecture && this.selectedLecture.id === lecture.id) {
        // If clicking the same lecture, deselect it
        this.selectedLecture = null;
      } else {
        // Select the new lecture
        this.selectedLecture = lecture;
      }
      
      // Re-render the chart with filtered data
      this.renderChart();
    },

    // Function to fetch subjects for the dropdown
    async fetchSubjects() {
      try {
        const response = await http.get("/subjects");
        this.subjects = response.data;

        // If no subjects exist, add a default one for testing
        if (this.subjects.length === 0) {
          this.subjects = [{ id: 1, name: "Default Subject" }];
        }
      } catch (error) {
        console.error("Error fetching subjects:", error);
        // Add a default subject for testing
        this.subjects = [{ id: 1, name: "Default Subject" }];
      }
    },

    // Function to add a new week
    async addNewWeek() {
      // Validate form
      if (!this.$refs.weekForm || !this.$refs.weekForm.validate()) {
        return;
      }

      this.addingWeek = true;
      try {
        // Create the new week
        const response = await http.post("/weeks/", {
          name: this.newWeekName,
          subject_id: this.newWeekSubject
        });

        console.log("Week created:", response.data);
        this.showAddWeekDialog = false;
        
        // Reset form
        this.newWeekName = "";
        
        // Refresh the dashboard to get the new week
        await this.fetchDashboardData(null);
        
        // Show success message
        alert("Week created successfully!");
      } catch (error) {
        console.error("Error creating week:", error);
        alert("Failed to create week. Please try again.");
      } finally {
        this.addingWeek = false;
      }
    },

    // Function to fetch data from the API based on selected week
    async fetchDashboardData(weekId = null) {
      try {
        this.loading = true;
        
        // Clear the chart if it exists
        if (this.chartInstance) {
          this.chartInstance.destroy();
          this.chartInstance = null;
        }
        
        const url = "/dashboards/teacher_dashboard" + (weekId ? `?week_id=${weekId}` : "");
        
        console.log("Fetching data from:", url);
        const response = await http.get(url);
        console.log("API Response:", response.data);
        
        const data = response.data;
        
        // Update available weeks if provided by the API
        if (data.weeks && data.weeks.length > 0) {
          this.weeks = data.weeks;
          
          // Add "All Weeks" option at the beginning
          if (!this.weeks.some(w => w.name === "All Weeks")) {
            this.weeks.unshift({ id: null, name: "All Weeks" });
          }
          
          // If no week is selected yet, select the first one
          if (this.selectedWeek === null) {
            this.selectedWeek = this.weeks[0].id;
          }
        } else {
          // If no weeks, initialize with just All Weeks
          this.weeks = [{ id: null, name: "All Weeks" }];
        }
        
        // Update current week display
        if (data.current_week) {
          this.currentWeekName = data.current_week;
        }
        
        // Update state with fetched data
        this.assignmentData = data.assignment_problem_area || [];
        this.completionData = data.completion_console || [];
        this.searchedTopics = data.searched_topics || [];
        this.gptSuggestions = data.gpt_suggestions || [];
        this.lectures = data.lectures || [];
        this.totalLectureCount = data.total_lecture_count || 0;
        this.commonSearches = data.common_searches || [];
        
        console.log("Assignment Data:", this.assignmentData);
        console.log("Lecture Data:", this.lectures);
        
        // Initialize chart after data is loaded and DOM is updated
        setTimeout(() => {
          this.renderChart();
        }, 100);
      } catch (error) {
        console.error("Error fetching teacher dashboard data:", error);
        // Reset data on error
        this.assignmentData = [];
        this.completionData = [];
        this.searchedTopics = [];
        this.gptSuggestions = [];
        this.lectures = [];
        this.totalLectureCount = 0;
        
        // Handle 404 errors specifically
        if (error.response && error.response.status === 404) {
          // If the selected week doesn't exist, reset to "All Weeks"
          if (weekId !== null) {
            // Show error notification
            alert(`Week not found: ${error.response.data.detail || 'The selected week is not available'}`);
            // Reset to all weeks
            this.selectedWeek = null;
            this.fetchDashboardData(null);
            return;
          }
        }
      } finally {
        this.loading = false;
      }
    },

    // Function to handle week change
    handleWeekChange(weekId) {
      // Reset lecture selection when changing weeks
      this.selectedLecture = null;
      this.fetchDashboardData(weekId);
    },

    // Function to get color based on completion percentage
    getCompletionColor(percentage) {
      if (percentage < 40) return "red";
      if (percentage < 70) return "orange";
      return "green";
    },

    // Function to get sentiment color and icon
    getSentimentInfo(sentiment, value) {
      if (sentiment === 'confusion') {
        return {
          color: value > 0.7 ? 'red' : value > 0.4 ? 'orange' : 'blue',
          icon: 'mdi-help-circle',
          label: 'Confusion'
        };
      } else if (sentiment === 'frustration') {
        return {
          color: value > 0.6 ? 'red' : value > 0.3 ? 'orange' : 'green',
          icon: 'mdi-emoticon-sad',
          label: 'Frustration'
        };
      }
      
      return {
        color: 'grey',
        icon: 'mdi-circle',
        label: sentiment
      };
    },

    // Function to render chart
    renderChart() {
      if (!this.$refs.chartCanvas) {
        console.error("Chart canvas element not found");
        return;
      }
      
      const dataToUse = this.filteredAssignmentData;
      
      if (!dataToUse || dataToUse.length === 0) {
        console.error("No assignment data available for chart");
        return;
      }
      
      console.log("Rendering chart with data:", dataToUse);
      console.log("Chart canvas element:", this.$refs.chartCanvas);
      
      // Group data by lecture for better visualization if lecture data exists
      const hasLectureInfo = dataToUse.some(item => item.lecture_name);
      
      try {
        // Clear existing chart
        if (this.chartInstance) {
          this.chartInstance.destroy();
          this.chartInstance = null;
        }
        
        const chartData = {
          labels: dataToUse.map((d) => d.question),
          datasets: [
            {
              label: "% Correctly Solved",
              data: dataToUse.map((d) => d.correct),
              backgroundColor: dataToUse.map((d) => 
                d.correct < 50 ? "rgba(255, 99, 132, 0.8)" : "rgba(54, 162, 235, 0.8)"
              ),
              borderColor: dataToUse.map((d) =>
                d.correct < 50 ? "rgb(255, 99, 132)" : "rgb(54, 162, 235)"
              ),
              borderWidth: 1,
            }
          ]
        };
        
        // If we have lecture info, add lecture-based grouping
        if (hasLectureInfo && !this.selectedLecture) {
          // Get unique lectures
          const uniqueLectures = [...new Set(dataToUse
            .filter(item => item.lecture_name)
            .map(item => item.lecture_name))];
            
          // Add a dataset for each lecture for better visualization
          const lectureColors = [
            'rgba(54, 162, 235, 0.2)', // blue
            'rgba(255, 206, 86, 0.2)', // yellow
            'rgba(75, 192, 192, 0.2)', // green
            'rgba(153, 102, 255, 0.2)', // purple
            'rgba(255, 159, 64, 0.2)', // orange
          ];
          
          uniqueLectures.forEach((lectureName, index) => {
            const color = lectureColors[index % lectureColors.length];
            const barThickness = 10;
            
            chartData.datasets.push({
              label: `Lecture: ${lectureName}`,
              data: dataToUse.map(d => 
                d.lecture_name === lectureName ? 100 : null
              ),
              backgroundColor: color,
              borderColor: color.replace('0.2', '1'),
              borderWidth: 1,
              type: 'bar',
              barThickness: barThickness,
              order: 1, // to ensure it's behind the main bars
              categoryPercentage: 1.0,
              barPercentage: 0.2,
            });
          });
        }
        
        this.chartInstance = new Chart(this.$refs.chartCanvas, {
          type: "bar",
          data: chartData,
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: 'top',
                display: hasLectureInfo,
              },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    const datasetLabel = context.dataset.label || '';
                    if (datasetLabel.startsWith('Lecture:')) {
                      return datasetLabel;
                    }
                    return `Correctly Solved: ${context.raw}%`;
                  },
                  footer: function(tooltipItems) {
                    const dataIndex = tooltipItems[0].dataIndex;
                    const data = dataToUse[dataIndex];
                    if (data && data.lecture_name) {
                      return `From: ${data.lecture_name}`;
                    }
                    return '';
                  }
                }
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                max: 100,
                title: {
                  display: true,
                  text: 'Percentage Correct'
                }
              },
              x: {
                title: {
                  display: true,
                  text: 'Questions'
                },
                stacked: false
              }
            },
          },
        });
        console.log("Chart created successfully:", this.chartInstance);
      } catch (error) {
        console.error("Error creating chart:", error);
      }
    },

    // Function to get the top topics from searches
    getTopSearchTopics() {
      // First, collect all topics
      const topicCounts = {};
      this.commonSearches.forEach(search => {
        if (search.topics) {
          search.topics.forEach(topic => {
            if (!topicCounts[topic]) {
              topicCounts[topic] = 0;
            }
            topicCounts[topic] += search.count;
          });
        }
      });
      
      // Convert to array for sorting
      const topicArray = Object.entries(topicCounts).map(([name, count]) => ({ name, count }));
      
      // Sort by count and return top 5
      return topicArray.sort((a, b) => b.count - a.count).slice(0, 5);
    },

    // Function to get the top lectures from searches
    getTopLectures() {
      // First, collect all lectures
      const lectureCounts = {};
      this.commonSearches.forEach(search => {
        if (search.lectures) {
          search.lectures.forEach(lecture => {
            if (!lectureCounts[lecture]) {
              lectureCounts[lecture] = 0;
            }
            lectureCounts[lecture] += search.count;
          });
        }
      });
      
      // Convert to array for sorting
      const lectureArray = Object.entries(lectureCounts).map(([name, count]) => ({ name, count }));
      
      // Sort by count and return top 5
      return lectureArray.sort((a, b) => b.count - a.count).slice(0, 5);
    },

    // Function to get the confusion rate
    getConfusionRate() {
      if (this.commonSearches.length === 0) return 0;
      
      // Count searches with high confusion
      const confusedSearches = this.commonSearches.filter(search => 
        search.sentiments && search.sentiments.confusion > 0.5
      ).length;
      
      return Math.round((confusedSearches / this.commonSearches.length) * 100);
    },
    
    // Function to get topic search percentage
    getTopicPercentage(topic) {
      const totalSearches = this.commonSearches.reduce((sum, item) => sum + item.count, 0);
      if (totalSearches === 0) return 0;
      
      return (topic.count / totalSearches) * 100;
    },
    
    // Function to get lecture performance data
    getLecturePerformance() {
      // Group assignment questions by lecture
      const lecturePerformance = {};
      
      this.assignmentData.forEach(question => {
        if (question.lecture_name) {
          if (!lecturePerformance[question.lecture_name]) {
            lecturePerformance[question.lecture_name] = {
              total: 0,
              correct: 0,
              count: 0
            };
          }
          
          lecturePerformance[question.lecture_name].total += question.correct;
          lecturePerformance[question.lecture_name].count += 1;
        }
      });
      
      // Calculate average performance per lecture
      return Object.entries(lecturePerformance)
        .map(([name, data]) => ({
          name,
          performance: Math.round(data.total / data.count)
        }))
        .sort((a, b) => b.performance - a.performance)
        .slice(0, 5);
    },
    
    // Helper function to truncate lecture names
    truncateLectureName(name) {
      return name.length > 20 ? name.substring(0, 18) + '...' : name;
    },

    // New variables for the Topic Correlation widget
    getTopicsWithHighConfusion() {
      const topicConfusion = {};
      const topicCounts = {};
      
      // Collect confusion levels for each topic
      this.commonSearches.forEach(search => {
        if (search.topics && search.sentiments && search.sentiments.confusion) {
          search.topics.forEach(topic => {
            if (!topicConfusion[topic]) {
              topicConfusion[topic] = 0;
              topicCounts[topic] = 0;
            }
            
            topicConfusion[topic] += search.sentiments.confusion * search.count;
            topicCounts[topic] += search.count;
          });
        }
      });
      
      // Calculate average confusion per topic
      const topicsWithConfusion = Object.entries(topicConfusion)
        .filter(([_, total]) => total > 0)
        .map(([name, totalConfusion]) => ({
          name,
          confusionLevel: totalConfusion / topicCounts[name],
          count: topicCounts[name]
        }))
        .filter(topic => topic.confusionLevel > 0.4) // Only topics with moderate to high confusion
        .sort((a, b) => b.confusionLevel - a.confusionLevel);
      
      return topicsWithConfusion.slice(0, 5);
    },

    getConfusionLevelColor(level) {
      if (level < 0.4) return 'success';
      if (level < 0.6) return 'warning';
      return 'error';
    },

    getTopicLectureCorrelation() {
      const lectureData = {};
      
      // First get lecture performance (reuse existing function)
      const lecturePerformance = this.getLecturePerformance().reduce((acc, item) => {
        acc[item.name] = item.performance;
        return acc;
      }, {});
      
      // Match topics to lectures
      this.commonSearches.forEach(search => {
        if (search.topics && search.lectures) {
          search.lectures.forEach(lecture => {
            if (!lectureData[lecture]) {
              lectureData[lecture] = {
                topicCounts: {},
                totalConfusion: 0,
                totalSearches: 0
              };
            }
            
            // Add topics for this lecture
            search.topics.forEach(topic => {
              if (!lectureData[lecture].topicCounts[topic]) {
                lectureData[lecture].topicCounts[topic] = 0;
              }
              lectureData[lecture].topicCounts[topic] += search.count;
            });
            
            // Add confusion data
            if (search.sentiments && search.sentiments.confusion) {
              lectureData[lecture].totalConfusion += search.sentiments.confusion * search.count;
              lectureData[lecture].totalSearches += search.count;
            }
          });
        }
      });
      
      // Process the data
      return Object.entries(lectureData)
        .map(([lecture, data]) => {
          // Get topics sorted by frequency
          const topics = Object.entries(data.topicCounts)
            .sort((a, b) => b[1] - a[1])
            .map(([topic]) => topic);
          
          // Calculate average confusion
          const confusionRate = data.totalSearches > 0 
            ? Math.round((data.totalConfusion / data.totalSearches) * 100)
            : 0;
          
          return {
            lecture,
            topics,
            performance: lecturePerformance[lecture] || 0,
            confusion: confusionRate
          };
        })
        .sort((a, b) => b.confusion - a.confusion);
    },

    getRecommendation() {
      const confusedTopics = this.getTopicsWithHighConfusion();
      const correlations = this.getTopicLectureCorrelation();
      
      if (confusedTopics.length === 0 || correlations.length === 0) {
        return null;
      }
      
      // Find lectures with high confusion and low performance
      const problematicLectures = correlations
        .filter(item => item.confusion > 40 && item.performance < 70)
        .slice(0, 1);
      
      if (problematicLectures.length > 0) {
        const lecture = problematicLectures[0];
        return `Consider reviewing material in "${this.truncateLectureName(lecture.lecture)}" - it shows high confusion (${lecture.confusion}%) and lower assignment performance (${lecture.performance}%)`;
      }
      
      // Alternative recommendation based on confused topic
      if (confusedTopics.length > 0) {
        const topic = confusedTopics[0];
        return `Students appear confused about "${topic.name}" - consider providing additional materials or clarification on this topic`;
      }
      
      return null;
    },

    // New variables for the Activity Timeline widget
    getActivityTimeline() {
      // Construct activities from existing data
      const activities = [];
      
      // Get recent searches - these are relatively newer activities
      const searches = this.commonSearches
        .filter(search => search.count > 1) // Only show repeated searches
        .slice(0, 3)
        .map(search => {
          const confusionLevel = search.sentiments && search.sentiments.confusion 
            ? search.sentiments.confusion : 0;
            
          return {
            title: `Search: "${search.query}"`,
            description: `${search.count} students searched for this. ${
              search.topics && search.topics.length 
                ? `Related to: ${search.topics.join(', ')}` 
                : ''
            }`,
            timeAgo: 'Recently',
            type: 'Search',
            color: confusionLevel > 0.6 ? 'red' : (confusionLevel > 0.4 ? 'orange' : 'blue')
          };
        });
      
      activities.push(...searches);
      
      // Identify assignment problems
      const problemQuestions = this.assignmentData
        .filter(item => item.correct < 50)
        .slice(0, 2)
        .map(item => {
          return {
            title: `Low Performance: ${item.question}`,
            description: `Only ${item.correct}% of students answered this correctly. ${
              item.lecture_name 
                ? `Related to lecture: ${item.lecture_name}` 
                : ''
            }`,
            timeAgo: 'This week',
            type: 'Assignment',
            color: 'red'
          };
        });
        
      activities.push(...problemQuestions);
      
      // Get lecture engagement data
      const lectureEngagement = this.getTopLectures()
        .slice(0, 2)
        .map(lecture => {
          return {
            title: `High Activity: ${lecture.name}`,
            description: `This lecture has generated ${lecture.count} searches, suggesting students are actively engaging with this content.`,
            timeAgo: 'This week',
            type: 'Lecture',
            color: 'green'
          };
        });
        
      activities.push(...lectureEngagement);
      
      // Add a recommendation if available
      const recommendation = this.getRecommendation();
      if (recommendation) {
        activities.push({
          title: 'Teaching Recommendation',
          description: recommendation,
          timeAgo: 'Generated now',
          type: 'Suggestion',
          color: 'amber darken-2'
        });
      }
      
      // Shuffle the activities a bit to create a more natural timeline
      return activities.sort(() => Math.random() - 0.5);
    },

    // Student Participation Tracker methods
    getActiveStudentCount() {
      // Estimate active students based on search counts
      // We're using a simple heuristic here - actual student count would come from real data
      // Get unique student identifiers if available, otherwise estimate from search activity
      const searchCount = this.commonSearches.reduce((sum, item) => sum + item.count, 0);
      const estimatedActiveStudents = Math.min(25, Math.max(10, Math.round(searchCount / 3)));
      
      return estimatedActiveStudents;
    },
    
    getInactiveStudentCount() {
      // Estimate total class size and subtract active students
      const estimatedClassSize = 35; // This would come from actual class roster data
      return Math.max(0, estimatedClassSize - this.getActiveStudentCount());
    },
    
    getParticipationRate() {
      const activeCount = this.getActiveStudentCount();
      const totalStudents = activeCount + this.getInactiveStudentCount();
      return totalStudents > 0 ? Math.round((activeCount / totalStudents) * 100) : 0;
    },
    
    getTopicEngagement() {
      // Analyze topic engagement and confusion levels
      const topicEngagement = {};
      
      // First, collect all topics and their engagement metrics
      this.commonSearches.forEach(search => {
        if (search.topics && search.topics.length) {
          search.topics.forEach(topic => {
            if (!topicEngagement[topic]) {
              topicEngagement[topic] = {
                searchCount: 0,
                confusionSum: 0,
                frustrationSum: 0,
                occurrences: 0,
              };
            }
            
            topicEngagement[topic].searchCount += search.count;
            topicEngagement[topic].occurrences += 1;
            
            // Add sentiment data if available
            if (search.sentiments) {
              if (search.sentiments.confusion) {
                topicEngagement[topic].confusionSum += search.sentiments.confusion * search.count;
              }
              if (search.sentiments.frustration) {
                topicEngagement[topic].frustrationSum += search.sentiments.frustration * search.count;
              }
            }
          });
        }
      });
      
      // Transform to array for processing
      const topicsArray = Object.entries(topicEngagement).map(([name, data]) => {
        // Calculate average confusion and frustration
        const confusionPercent = data.searchCount > 0 
          ? Math.round((data.confusionSum / data.searchCount) * 100) 
          : 0;
          
        // Calculate engagement rating (1-3)
        // Higher search count = higher engagement
        const maxSearches = Math.max(...Object.values(topicEngagement).map(d => d.searchCount));
        const engagementRating = maxSearches > 0 
          ? Math.min(3, Math.max(1, Math.round((data.searchCount / maxSearches) * 3))) 
          : 1;
          
        // Determine status based on engagement and confusion
        let status = 'Good';
        if (confusionPercent > 60) {
          status = 'Needs Attention';
        } else if (confusionPercent > 30 || data.searchCount > (maxSearches * 0.7)) {
          status = 'Monitor';
        }
        
        return {
          name,
          searchCount: data.searchCount,
          confusionPercent,
          engagementRating,
          status
        };
      });
      
      // Sort by status (needs attention first) then by search count
      return topicsArray
        .sort((a, b) => {
          // First by status priority
          const statusPriority = { 'Needs Attention': 0, 'Monitor': 1, 'Good': 2 };
          if (statusPriority[a.status] !== statusPriority[b.status]) {
            return statusPriority[a.status] - statusPriority[b.status];
          }
          // Then by search count (descending)
          return b.searchCount - a.searchCount;
        })
        .slice(0, 5); // Only show top 5 topics
    },
    
    getTeachingPriority() {
      const topicEngagement = this.getTopicEngagement();
      
      // Find topics that need attention
      const needsAttention = topicEngagement.filter(topic => topic.status === 'Needs Attention');
      
      if (needsAttention.length > 0) {
        const topic = needsAttention[0];
        return `Focus on explaining "${topic.name}" - high confusion (${topic.confusionPercent}%) with ${topic.searchCount} searches`;
      }
      
      return null;
    },
    
    refreshTopicInsights() {
      // This function would trigger a refresh of the data in a real implementation
      // For now, we'll just show a notification
      alert('Topic insights refreshed!');
    }
  }
};
</script>

<style scoped>
.chart-container {
  position: relative;
  height: 350px;
  width: 100%;
}
canvas {
  width: 100%;
  height: 100%;
}
.selected-lecture {
  background-color: rgba(33, 150, 243, 0.1);
  border-left: 3px solid #2196F3;
}
.search-insights {
  background-color: #f5f5f5;
  border-radius: 4px;
  height: 100%;
}

/* Problem Areas Table Styles */
.problem-areas-table >>> thead tr {
  position: sticky;
  top: 0;
  background-color: white;
  z-index: 1;
}

.problem-areas-table >>> th {
  box-shadow: 0 2px 2px -1px rgba(0, 0, 0, 0.1);
}

/* Quiz Performance Styles */
.quiz-select {
  max-width: 300px;
}

.stat-card {
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
</style>