import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { 
  BookOpen, 
  Users, 
  CheckCircle, 
  Star,
  Plus,
  Edit,
  Trash2
} from 'lucide-react'

const Lessons = () => {
  const [lessons, setLessons] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchLessons()
  }, [])

  const fetchLessons = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const response = await fetch('http://localhost:5001/api/admin/lessons', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      const data = await response.json()
      if (data.success) {
        setLessons(data.lessons)
      }
    } catch (error) {
      console.error('Error fetching lessons:', error)
    } finally {
      setLoading(false)
    }
  }

  const getLevelBadge = (level) => {
    const levels = {
      'beginner': { label: 'مبتدئ', color: 'bg-green-100 text-green-800' },
      'intermediate': { label: 'متوسط', color: 'bg-yellow-100 text-yellow-800' },
      'advanced': { label: 'متقدم', color: 'bg-red-100 text-red-800' }
    }
    
    const levelInfo = levels[level] || levels['beginner']
    return (
      <Badge className={levelInfo.color}>
        {levelInfo.label}
      </Badge>
    )
  }

  const getCompletionRate = (enrolled, completed) => {
    if (enrolled === 0) return 0
    return Math.round((completed / enrolled) * 100)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">إدارة الدروس</h1>
          <p className="text-gray-500">إدارة المحتوى التعليمي والدروس</p>
        </div>
        <Button className="bg-blue-600 hover:bg-blue-700">
          <Plus className="w-4 h-4 mr-2" />
          إضافة درس جديد
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">إجمالي الدروس</p>
                <p className="text-2xl font-bold text-gray-900">{lessons.length}</p>
              </div>
              <BookOpen className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">دروس المبتدئين</p>
                <p className="text-2xl font-bold text-green-600">
                  {lessons.filter(l => l.level === 'beginner').length}
                </p>
              </div>
              <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                <span className="text-green-600 font-bold">1</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">دروس متوسطة</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {lessons.filter(l => l.level === 'intermediate').length}
                </p>
              </div>
              <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                <span className="text-yellow-600 font-bold">2</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">دروس متقدمة</p>
                <p className="text-2xl font-bold text-red-600">
                  {lessons.filter(l => l.level === 'advanced').length}
                </p>
              </div>
              <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                <span className="text-red-600 font-bold">3</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Lessons Table */}
      <Card>
        <CardHeader>
          <CardTitle>قائمة الدروس</CardTitle>
          <CardDescription>
            جميع الدروس المتاحة في النظام
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>الدرس</TableHead>
                <TableHead>المستوى</TableHead>
                <TableHead>النقاط</TableHead>
                <TableHead>المشتركين</TableHead>
                <TableHead>معدل الإكمال</TableHead>
                <TableHead>النوع</TableHead>
                <TableHead>الإجراءات</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {lessons.map((lesson) => (
                <TableRow key={lesson.id}>
                  <TableCell>
                    <div className="space-y-1">
                      <p className="font-medium text-gray-900">{lesson.title_ar}</p>
                      <p className="text-sm text-gray-500">{lesson.title_en}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    {getLevelBadge(lesson.level)}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-1">
                      <Star className="w-4 h-4 text-yellow-500" />
                      <span className="font-medium">{lesson.points_reward}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-1">
                      <Users className="w-4 h-4 text-blue-500" />
                      <span>{lesson.enrolled_users}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full" 
                          style={{ 
                            width: `${getCompletionRate(lesson.enrolled_users, lesson.completed_users)}%` 
                          }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">
                        {getCompletionRate(lesson.enrolled_users, lesson.completed_users)}%
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    {lesson.is_premium ? (
                      <Badge className="bg-purple-100 text-purple-800">
                        مميز
                      </Badge>
                    ) : (
                      <Badge variant="secondary">مجاني</Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Button variant="outline" size="sm">
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Popular Lessons */}
      <Card>
        <CardHeader>
          <CardTitle>الدروس الأكثر شعبية</CardTitle>
          <CardDescription>
            الدروس التي حققت أعلى معدلات المشاركة والإكمال
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {lessons
              .sort((a, b) => b.enrolled_users - a.enrolled_users)
              .slice(0, 5)
              .map((lesson, index) => (
                <div key={lesson.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                      <span className="text-blue-600 font-bold">{index + 1}</span>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{lesson.title_ar}</p>
                      <p className="text-sm text-gray-500">
                        {lesson.enrolled_users} مشترك • {lesson.completed_users} مكتمل
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {getLevelBadge(lesson.level)}
                    <div className="flex items-center space-x-1">
                      <CheckCircle className="w-4 h-4 text-green-500" />
                      <span className="text-sm font-medium">
                        {getCompletionRate(lesson.enrolled_users, lesson.completed_users)}%
                      </span>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Lessons

