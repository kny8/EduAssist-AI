<template>
    <div class="student-dashboard">
      <h1>Student Dashboard: Bookmarks View</h1>
      <div class="container">
<!--        <div class="sidebar">-->
<!--          <p>Jan'25<br>Software Engg.</p>-->
<!--          <button>Homepage</button>-->
<!--          <button>Study with GenAI</button>-->
<!--          <button>Code with GenAI</button>-->
<!--          <button class="active">Bookmarks</button>-->
<!--          <button>To Course Page</button>-->
<!--        </div>-->
        <div class="content">
          <h2>Your bookmarks</h2>
          <div class="bookmarks-list">
            <div class="bookmark-item">
              <p>Topic: ABC | Week: 1</p>
              <button>Go To Lecture</button>
              <button>Go To PDF</button>
            </div>
            <div class="bookmark-item">
              <p>Topic: ABC | Week: 1</p>
              <button>Go To Lecture</button>
              <button>Go To PDF</button>
            </div>
            <div class="bookmark-item">
              <p>Topic: ABC | Week: 1</p>
              <button>Go To Lecture</button>
              <button>Go To PDF</button>
            </div>
          </div>
        </div>
        <div class="right-panel">
          <div class="global-search">
            <h3>Global Search</h3>
            <input type="text" placeholder="Search">
            <button>🔍</button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'BookmarkPage',
  };
  </script>
  
  <style scoped>
  .student-dashboard {
    font-family: Arial, sans-serif;
    padding: 20px;
  }
  
  .container {
    display: flex;
    gap: 20px;
  }
  
  .sidebar {
    display: flex;
    flex-direction: column;
    width: 150px;
  }
  
  .sidebar button {
    padding: 10px;
    margin-bottom: 5px;
    border: 1px solid #ddd;
    background-color: #f9f9f9;
    cursor: pointer;
  }
  
  .sidebar button.active {
    background-color: #e0e0e0;
  }
  
  .content {
    flex: 2;
  }
  
  .content h2 {
    margin-bottom: 20px;
  }
  
  .bookmarks-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .bookmark-item {
    border: 1px solid #ddd;
    padding: 10px;
  }
  
  .bookmark-item button {
    margin-left: 10px;
    padding: 5px 10px;
    cursor: pointer;
  }
  
  .right-panel {
    flex: 1;
  }
  
  .global-search {
    border: 1px solid #ddd;
    padding: 10px;
  }
  
  .global-search input {
    padding: 5px;
  }
  </style>
  