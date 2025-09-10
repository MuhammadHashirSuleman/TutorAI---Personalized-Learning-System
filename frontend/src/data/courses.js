// Premium course database with courses from top platforms
export const courseDatabase = {
  'computer-science': [
    {
      id: 'cs-1',
      title: 'Introduction to Computer Science',
      provider: 'Coursera',
      instructor: 'Dr. David J. Malan',
      description: 'This is CS50x, Harvard University\'s introduction to the intellectual enterprises of computer science and the art of programming.',
      thumbnail: 'https://img.freepik.com/free-vector/programming-concept-illustration_114360-1351.jpg',
      duration: '12 weeks',
      level: 'Beginner',
      rating: 4.8,
      students: 125000,
      topics: ['Programming', 'Algorithms', 'Data Structures', 'C', 'Python', 'SQL'],
      url: 'https://www.coursera.org/learn/cs50-introduction-computer-science',
      free: true,
      category: 'Programming'
    },
    {
      id: 'cs-2',
      title: 'CUDA Programming Fundamentals',
      provider: 'NVIDIA',
      instructor: 'NVIDIA Deep Learning Institute',
      description: 'Learn parallel programming with CUDA C/C++. Master GPU acceleration for high-performance computing.',
      thumbnail: 'https://img.freepik.com/free-vector/gpu-concept-illustration_114360-8891.jpg',
      duration: '8 hours',
      level: 'Intermediate',
      rating: 4.9,
      students: 45000,
      topics: ['CUDA', 'Parallel Programming', 'GPU Computing', 'Memory Management', 'Optimization'],
      url: 'https://courses.nvidia.com/courses/course-v1:DLI+C-AC-01+V1/',
      free: true,
      category: 'GPU Programming'
    },
    {
      id: 'cs-3',
      title: 'Deep Learning for Computer Vision',
      provider: 'NVIDIA',
      instructor: 'NVIDIA Deep Learning Institute',
      description: 'Build and deploy neural networks for image classification, object detection, and image segmentation.',
      thumbnail: 'https://img.freepik.com/free-vector/computer-vision-concept-illustration_114360-4567.jpg',
      duration: '8 hours',
      level: 'Advanced',
      rating: 4.8,
      students: 67000,
      topics: ['CNNs', 'Object Detection', 'Image Segmentation', 'Transfer Learning', 'TensorFlow'],
      url: 'https://courses.nvidia.com/courses/course-v1:DLI+C-CV-01+V1/',
      free: true,
      category: 'Computer Vision'
    },
    {
      id: 'cs-4',
      title: 'Machine Learning Course',
      provider: 'Coursera',
      instructor: 'Andrew Ng',
      description: 'Machine Learning course by Stanford University. Learn about supervised and unsupervised learning.',
      thumbnail: 'https://img.freepik.com/free-vector/machine-learning-banner-web-icon-set_603843-3838.jpg',
      duration: '11 weeks',
      level: 'Intermediate',
      rating: 4.9,
      students: 2800000,
      topics: ['Linear Regression', 'Neural Networks', 'SVM', 'Clustering', 'Python'],
      url: 'https://www.coursera.org/learn/machine-learning',
      free: true,
      category: 'Machine Learning'
    },
    {
      id: 'cs-5',
      title: 'Python Complete Bootcamp',
      provider: 'Udemy',
      instructor: 'Jose Portilla',
      description: 'Complete Python course from beginner to advanced with real-world projects and exercises.',
      thumbnail: 'https://img.freepik.com/free-vector/programming-concept-banner_1284-41269.jpg',
      duration: '22 hours',
      level: 'Beginner to Advanced',
      rating: 4.6,
      students: 1850000,
      topics: ['Python', 'OOP', 'Web Scraping', 'GUI Development', 'Data Analysis'],
      url: 'https://www.udemy.com/course/complete-python-bootcamp/',
      free: true,
      category: 'Programming'
    },
    {
      id: 'cs-6',
      title: 'Natural Language Processing',
      provider: 'NVIDIA',
      instructor: 'NVIDIA Deep Learning Institute',
      description: 'Learn to build and deploy neural networks for natural language processing tasks.',
      thumbnail: 'https://img.freepik.com/free-vector/nlp-concept-illustration_114360-7789.jpg',
      duration: '8 hours',
      level: 'Advanced',
      rating: 4.7,
      students: 32000,
      topics: ['NLP', 'Transformers', 'BERT', 'Text Classification', 'Named Entity Recognition'],
      url: 'https://courses.nvidia.com/courses/course-v1:DLI+S-FX-07+V1/',
      free: true,
      category: 'NLP'
    }
  ],
  'mathematics': [
    {
      id: 'math-1',
      title: 'Mathematics for Machine Learning',
      provider: 'Coursera',
      instructor: 'Imperial College London',
      description: 'Learn the essential mathematics for machine learning: linear algebra, multivariate calculus, and PCA.',
      thumbnail: 'https://img.freepik.com/free-vector/mathematics-concept-illustration_114360-1115.jpg',
      duration: '4 months',
      level: 'Intermediate',
      rating: 4.6,
      students: 89000,
      topics: ['Linear Algebra', 'Multivariate Calculus', 'PCA', 'Eigenvalues', 'Statistics'],
      url: 'https://www.coursera.org/specializations/mathematics-machine-learning',
      free: true,
      category: 'Applied Mathematics'
    },
    {
      id: 'math-2',
      title: 'Data Science Math Skills',
      provider: 'Coursera',
      instructor: 'Duke University',
      description: 'Master the math fundamentals needed for data science and machine learning.',
      thumbnail: 'https://img.freepik.com/free-vector/mathematics-algebra-word-concepts-banner_107791-3640.jpg',
      duration: '4 weeks',
      level: 'Beginner',
      rating: 4.7,
      students: 156000,
      topics: ['Set Theory', 'Functions', 'Algebra', 'Probability', 'Statistics'],
      url: 'https://www.coursera.org/learn/datasciencemathskills',
      free: true,
      category: 'Data Science Math'
    },
    {
      id: 'math-3',
      title: 'Statistics Fundamentals',
      provider: 'Microsoft',
      instructor: 'Microsoft Learn',
      description: 'Introduction to statistics for data analysis and business intelligence.',
      thumbnail: 'https://img.freepik.com/free-vector/statistics-concept-illustration_114360-1283.jpg',
      duration: '12 hours',
      level: 'Beginner',
      rating: 4.5,
      students: 67000,
      topics: ['Descriptive Statistics', 'Probability', 'Hypothesis Testing', 'Regression', 'Excel'],
      url: 'https://docs.microsoft.com/learn/paths/explore-analyze-data-with-r/',
      free: true,
      category: 'Statistics'
    }
  ],
  'science': [
    {
      id: 'sci-1',
      title: 'Introduction to Biology',
      provider: 'Coursera',
      instructor: 'Prof. Eric Lander',
      description: 'Explore the fundamental principles of biology, from molecular mechanisms to ecosystems.',
      thumbnail: 'https://img.freepik.com/free-vector/science-word-theme-with-biology-equipments_1308-48150.jpg',
      duration: '15 weeks',
      level: 'Beginner',
      rating: 4.4,
      students: 78000,
      topics: ['Cell Biology', 'Genetics', 'Evolution', 'Ecology', 'Molecular Biology'],
      url: 'https://www.coursera.org/learn/introduction-to-biology',
      free: true,
      category: 'Biology'
    },
    {
      id: 'sci-2',
      title: 'Physics I: Classical Mechanics',
      provider: 'Coursera',
      instructor: 'Prof. Walter Lewin',
      description: 'Learn the fundamental concepts of classical mechanics through engaging lectures and demonstrations.',
      thumbnail: 'https://img.freepik.com/free-vector/physics-concept-illustration_114360-1112.jpg',
      duration: '12 weeks',
      level: 'Intermediate',
      rating: 4.8,
      students: 145000,
      topics: ['Kinematics', 'Dynamics', 'Energy', 'Momentum', 'Oscillations', 'Waves'],
      url: 'https://www.coursera.org/learn/physics-classical-mechanics',
      free: true,
      category: 'Physics'
    },
    {
      id: 'sci-3',
      title: 'Data Science with Python',
      provider: 'Udemy',
      instructor: 'Jose Portilla',
      description: 'Learn data science using Python with pandas, matplotlib, seaborn, plotly, scikit-learn and more.',
      thumbnail: 'https://img.freepik.com/free-vector/data-science-concept-illustration_114360-1234.jpg',
      duration: '25 hours',
      level: 'Beginner to Advanced',
      rating: 4.6,
      students: 892000,
      topics: ['Python', 'Pandas', 'NumPy', 'Matplotlib', 'Machine Learning', 'Data Visualization'],
      url: 'https://www.udemy.com/course/python-for-data-science-and-machine-learning-bootcamp/',
      free: true,
      category: 'Data Science'
    }
  ],
  'business': [
    {
      id: 'bus-1',
      title: 'Strategic Leadership and Management',
      provider: 'LinkedIn Learning',
      instructor: 'Mike Figliuolo',
      description: 'Learn essential leadership skills to drive organizational success and manage high-performing teams.',
      thumbnail: 'https://img.freepik.com/free-vector/marketing-concept-illustration_114360-1293.jpg',
      duration: '2 hours',
      level: 'Intermediate',
      rating: 4.6,
      students: 234000,
      topics: ['Leadership', 'Team Management', 'Strategic Planning', 'Decision Making', 'Communication'],
      url: 'https://www.linkedin.com/learning/strategic-leadership-and-management',
      free: true,
      category: 'Leadership'
    },
    {
      id: 'bus-2',
      title: 'Financial Markets',
      provider: 'Coursera',
      instructor: 'Prof. Robert Shiller',
      description: 'Overview of ideas, methods, and institutions that permit human society to manage risks.',
      thumbnail: 'https://img.freepik.com/free-vector/finance-concept-illustration_114360-1276.jpg',
      duration: '7 weeks',
      level: 'Intermediate',
      rating: 4.5,
      students: 456000,
      topics: ['Investment', 'Insurance', 'Banking', 'Behavioral Finance', 'Risk Management'],
      url: 'https://www.coursera.org/learn/financial-markets-global',
      free: true,
      category: 'Finance'
    },
    {
      id: 'bus-3',
      title: 'Digital Marketing Fundamentals',
      provider: 'LinkedIn Learning',
      instructor: 'Brad Batesole',
      description: 'Master the foundations of digital marketing including SEO, social media, and content marketing.',
      thumbnail: 'https://img.freepik.com/free-vector/business-startup-concept-illustration_114360-1285.jpg',
      duration: '3 hours',
      level: 'Beginner',
      rating: 4.7,
      students: 189000,
      topics: ['SEO', 'Social Media', 'Content Marketing', 'Analytics', 'PPC Advertising'],
      url: 'https://www.linkedin.com/learning/digital-marketing-foundations',
      free: true,
      category: 'Digital Marketing'
    },
    {
      id: 'bus-4',
      title: 'Project Management Fundamentals',
      provider: 'Microsoft',
      instructor: 'Microsoft Learn',
      description: 'Learn project management essentials using Microsoft Project and modern PM methodologies.',
      thumbnail: 'https://img.freepik.com/free-vector/project-management-concept_23-2148479591.jpg',
      duration: '8 hours',
      level: 'Beginner',
      rating: 4.4,
      students: 123000,
      topics: ['Project Planning', 'Resource Management', 'Risk Assessment', 'Agile', 'Microsoft Project'],
      url: 'https://docs.microsoft.com/learn/paths/manage-projects-with-microsoft-project/',
      free: true,
      category: 'Project Management'
    }
  ],
  'languages': [
    {
      id: 'lang-1',
      title: 'Spanish for Business',
      provider: 'Coursera',
      instructor: 'Universidad de Palermo',
      description: 'Learn Spanish language skills specifically for business and professional contexts.',
      thumbnail: 'https://img.freepik.com/free-vector/language-learning-concept-illustration_114360-1313.jpg',
      duration: '8 weeks',
      level: 'Beginner',
      rating: 4.4,
      students: 89000,
      topics: ['Business Vocabulary', 'Professional Communication', 'Presentations', 'Email Writing', 'Meetings'],
      url: 'https://www.coursera.org/learn/spanish-business',
      free: true,
      category: 'Spanish'
    },
    {
      id: 'lang-2',
      title: 'English Grammar and Style',
      provider: 'Coursera',
      instructor: 'Prof. Roslyn Petelin',
      description: 'Improve your English writing skills and learn advanced grammar concepts.',
      thumbnail: 'https://img.freepik.com/free-vector/english-concept-illustration_114360-1199.jpg',
      duration: '8 weeks',
      level: 'Intermediate',
      rating: 4.3,
      students: 167000,
      topics: ['Grammar Rules', 'Writing Style', 'Punctuation', 'Sentence Structure', 'Academic Writing'],
      url: 'https://www.coursera.org/learn/grammar-punctuation',
      free: true,
      category: 'English'
    },
    {
      id: 'lang-3',
      title: 'Technical Writing Fundamentals',
      provider: 'LinkedIn Learning',
      instructor: 'Judy Steiner-Williams',
      description: 'Learn to write clear, concise technical documentation and communications.',
      thumbnail: 'https://img.freepik.com/free-vector/technical-writing-concept_23-2148479591.jpg',
      duration: '2.5 hours',
      level: 'Beginner',
      rating: 4.5,
      students: 78000,
      topics: ['Technical Documentation', 'Clear Writing', 'User Manuals', 'API Documentation', 'Process Writing'],
      url: 'https://www.linkedin.com/learning/technical-writing-fundamentals',
      free: true,
      category: 'Technical Writing'
    }
  ],
  'arts': [
    {
      id: 'arts-1',
      title: 'Introduction to Art History',
      provider: 'Coursera',
      instructor: 'Prof. Sharon Waxman',
      description: 'Explore the history of art from ancient civilizations to modern times.',
      thumbnail: 'https://img.freepik.com/free-vector/art-concept-illustration_114360-1287.jpg',
      duration: '10 weeks',
      level: 'Beginner',
      rating: 4.5,
      students: 78000,
      topics: ['Renaissance Art', 'Modern Art', 'Ancient Art', 'Art Movements', 'Critical Analysis'],
      url: 'https://www.coursera.org/learn/art-history',
      free: true,
      category: 'Art History'
    },
    {
      id: 'arts-2',
      title: 'Creative Writing Specialization',
      provider: 'Coursera',
      instructor: 'Prof. Brando Skyhorse',
      description: 'Develop your creative writing skills across different genres and forms.',
      thumbnail: 'https://img.freepik.com/free-vector/creative-writing-concept-illustration_114360-1272.jpg',
      duration: '5 months',
      level: 'Beginner',
      rating: 4.6,
      students: 123000,
      topics: ['Fiction Writing', 'Poetry', 'Creative Nonfiction', 'Character Development', 'Plot Structure'],
      url: 'https://www.coursera.org/specializations/creative-writing',
      free: true,
      category: 'Creative Writing'
    },
    {
      id: 'arts-3',
      title: 'Complete Digital Drawing Course',
      provider: 'Udemy',
      instructor: 'Robin Slee',
      description: 'Master digital drawing and illustration with comprehensive training in digital art techniques.',
      thumbnail: 'https://img.freepik.com/free-vector/digital-art-concept-illustration_114360-5678.jpg',
      duration: '18 hours',
      level: 'Beginner',
      rating: 4.7,
      students: 145000,
      topics: ['Digital Drawing', 'Illustration', 'Character Design', 'Color Theory', 'Digital Painting', 'Adobe Photoshop'],
      url: 'https://www.udemy.com/course/complete-digital-drawing-course/',
      free: true,
      category: 'Digital Art'
    }
  ]
};

// Function to get courses by field
export const getCoursesByField = (field) => {
  return courseDatabase[field] || [];
};

// Function to get all courses
export const getAllCourses = () => {
  return Object.values(courseDatabase).flat();
};

// Function to get course by ID
export const getCourseById = (id) => {
  const allCourses = getAllCourses();
  return allCourses.find(course => course.id === id);
};

// Function to search courses
export const searchCourses = (query, field = null) => {
  const courses = field ? getCoursesByField(field) : getAllCourses();
  return courses.filter(course => 
    course.title.toLowerCase().includes(query.toLowerCase()) ||
    course.description.toLowerCase().includes(query.toLowerCase()) ||
    course.topics.some(topic => topic.toLowerCase().includes(query.toLowerCase()))
  );
};

// Function to get recommended courses based on user progress
export const getRecommendedCourses = (userField, completedCourses = []) => {
  const fieldCourses = getCoursesByField(userField);
  const otherCourses = getAllCourses().filter(course => 
    !fieldCourses.includes(course) && !completedCourses.includes(course.id)
  );
  
  // Return field-specific courses first, then some from other fields
  return [...fieldCourses.slice(0, 6), ...otherCourses.slice(0, 2)];
};

export default courseDatabase;
