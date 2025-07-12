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
  Newspaper, 
  AlertTriangle, 
  Shield, 
  Bug,
  Plus,
  Edit,
  Trash2,
  ExternalLink,
  Calendar
} from 'lucide-react'

const News = () => {
  const [news, setNews] = useState([])
  const [loading, setLoading] = useState(true)
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
    pages: 0
  })

  useEffect(() => {
    fetchNews()
  }, [pagination.page])

  const fetchNews = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const params = new URLSearchParams({
        page: pagination.page,
        limit: pagination.limit
      })

      const response = await fetch(`http://localhost:5001/api/admin/news?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      const data = await response.json()
      if (data.success) {
        setNews(data.news)
        setPagination(prev => ({
          ...prev,
          total: data.pagination.total,
          pages: data.pagination.pages
        }))
      }
    } catch (error) {
      console.error('Error fetching news:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSeverityBadge = (severity) => {
    const severities = {
      'critical': { 
        label: 'حرج', 
        color: 'bg-red-100 text-red-800',
        icon: AlertTriangle
      },
      'high': { 
        label: 'عالي', 
        color: 'bg-orange-100 text-orange-800',
        icon: Shield
      },
      'medium': { 
        label: 'متوسط', 
        color: 'bg-yellow-100 text-yellow-800',
        icon: Bug
      },
      'low': { 
        label: 'منخفض', 
        color: 'bg-green-100 text-green-800',
        icon: Shield
      }
    }
    
    const severityInfo = severities[severity] || severities['medium']
    const Icon = severityInfo.icon
    
    return (
      <Badge className={severityInfo.color}>
        <Icon className="w-3 h-3 mr-1" />
        {severityInfo.label}
      </Badge>
    )
  }

  const getCategoryBadge = (category) => {
    const categories = {
      'critical': { label: 'تنبيه حرج', color: 'bg-red-100 text-red-800' },
      'vulnerability': { label: 'ثغرة أمنية', color: 'bg-purple-100 text-purple-800' },
      'malware': { label: 'برمجية خبيثة', color: 'bg-orange-100 text-orange-800' },
      'threat': { label: 'تهديد', color: 'bg-yellow-100 text-yellow-800' },
      'general': { label: 'عام', color: 'bg-gray-100 text-gray-800' }
    }
    
    const categoryInfo = categories[category] || categories['general']
    return (
      <Badge className={categoryInfo.color}>
        {categoryInfo.label}
      </Badge>
    )
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ar-SA', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getNewsStats = () => {
    const stats = {
      total: news.length,
      critical: news.filter(n => n.severity === 'critical').length,
      vulnerabilities: news.filter(n => n.category === 'vulnerability').length,
      malware: news.filter(n => n.category === 'malware').length,
      featured: news.filter(n => n.is_featured).length
    }
    return stats
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const stats = getNewsStats()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">إدارة الأخبار</h1>
          <p className="text-gray-500">إدارة الأخبار الأمنية والتنبيهات</p>
        </div>
        <Button className="bg-blue-600 hover:bg-blue-700">
          <Plus className="w-4 h-4 mr-2" />
          إضافة خبر جديد
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">إجمالي الأخبار</p>
                <p className="text-2xl font-bold text-gray-900">{pagination.total}</p>
              </div>
              <Newspaper className="w-8 h-8 text-blue-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">تنبيهات حرجة</p>
                <p className="text-2xl font-bold text-red-600">{stats.critical}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">ثغرات أمنية</p>
                <p className="text-2xl font-bold text-purple-600">{stats.vulnerabilities}</p>
              </div>
              <Shield className="w-8 h-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">برمجيات خبيثة</p>
                <p className="text-2xl font-bold text-orange-600">{stats.malware}</p>
              </div>
              <Bug className="w-8 h-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">أخبار مميزة</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.featured}</p>
              </div>
              <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                <span className="text-yellow-600 text-lg">⭐</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* News Table */}
      <Card>
        <CardHeader>
          <CardTitle>قائمة الأخبار</CardTitle>
          <CardDescription>
            جميع الأخبار الأمنية المنشورة في النظام
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>العنوان</TableHead>
                <TableHead>التصنيف</TableHead>
                <TableHead>الخطورة</TableHead>
                <TableHead>تاريخ النشر</TableHead>
                <TableHead>الحالة</TableHead>
                <TableHead>الإجراءات</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {news.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>
                    <div className="space-y-1 max-w-md">
                      <p className="font-medium text-gray-900 line-clamp-2">
                        {item.title_ar}
                      </p>
                      <p className="text-sm text-gray-500 line-clamp-1">
                        {item.title_en}
                      </p>
                    </div>
                  </TableCell>
                  <TableCell>
                    {getCategoryBadge(item.category)}
                  </TableCell>
                  <TableCell>
                    {getSeverityBadge(item.severity)}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <span className="text-sm">{formatDate(item.published_date)}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      {item.is_featured && (
                        <Badge className="bg-yellow-100 text-yellow-800">
                          مميز
                        </Badge>
                      )}
                      <Badge variant="secondary">منشور</Badge>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Button variant="outline" size="sm">
                        <Edit className="w-4 h-4" />
                      </Button>
                      <Button variant="outline" size="sm">
                        <ExternalLink className="w-4 h-4" />
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

          {/* Pagination */}
          <div className="flex items-center justify-between mt-4">
            <p className="text-sm text-gray-500">
              عرض {((pagination.page - 1) * pagination.limit) + 1} إلى {Math.min(pagination.page * pagination.limit, pagination.total)} من {pagination.total}
            </p>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
                disabled={pagination.page === 1}
              >
                السابق
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
                disabled={pagination.page === pagination.pages}
              >
                التالي
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Critical News */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-red-500" />
            <span>التنبيهات الحرجة الأخيرة</span>
          </CardTitle>
          <CardDescription>
            أهم التنبيهات الأمنية الحرجة التي تحتاج متابعة فورية
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {news
              .filter(item => item.severity === 'critical')
              .slice(0, 5)
              .map((item) => (
                <div key={item.id} className="flex items-center justify-between p-4 bg-red-50 border border-red-200 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <AlertTriangle className="w-6 h-6 text-red-500" />
                    <div>
                      <p className="font-medium text-gray-900">{item.title_ar}</p>
                      <p className="text-sm text-gray-500">{formatDate(item.published_date)}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {getCategoryBadge(item.category)}
                    <Button variant="outline" size="sm">
                      <ExternalLink className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default News

