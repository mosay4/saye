import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { 
  Users, 
  BookOpen, 
  Star, 
  Newspaper, 
  ShoppingCart, 
  DollarSign,
  TrendingUp,
  Activity
} from 'lucide-react'

const Dashboard = () => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardStats()
  }, [])

  const fetchDashboardStats = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const response = await fetch('http://localhost:5001/api/admin/dashboard', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      const data = await response.json()
      if (data.success) {
        setStats(data.stats)
      }
    } catch (error) {
      console.error('Error fetching dashboard stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const statCards = [
    {
      title: 'إجمالي المستخدمين',
      value: stats?.users?.total || 0,
      description: `${stats?.users?.new_today || 0} مستخدم جديد اليوم`,
      icon: Users,
      color: 'bg-blue-500',
      trend: '+12%'
    },
    {
      title: 'أعضاء VIP',
      value: stats?.users?.vip || 0,
      description: 'الأعضاء المميزين',
      icon: Star,
      color: 'bg-yellow-500',
      trend: '+8%'
    },
    {
      title: 'الدروس المكتملة',
      value: stats?.lessons?.completed || 0,
      description: `من أصل ${stats?.lessons?.total || 0} درس`,
      icon: BookOpen,
      color: 'bg-green-500',
      trend: '+15%'
    },
    {
      title: 'إجمالي النقاط',
      value: stats?.points?.total || 0,
      description: `${stats?.points?.transactions || 0} معاملة`,
      icon: Activity,
      color: 'bg-purple-500',
      trend: '+25%'
    },
    {
      title: 'الأخبار المنشورة',
      value: stats?.news?.total || 0,
      description: `${stats?.news?.today || 0} خبر اليوم`,
      icon: Newspaper,
      color: 'bg-indigo-500',
      trend: '+5%'
    },
    {
      title: 'المشتريات',
      value: stats?.shop?.purchases || 0,
      description: `$${stats?.shop?.revenue || 0} إيرادات`,
      icon: ShoppingCart,
      color: 'bg-pink-500',
      trend: '+18%'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg p-6 text-white">
        <h1 className="text-3xl font-bold mb-2">مرحباً بك في لوحة التحكم</h1>
        <p className="text-blue-100">
          إدارة شاملة لنظام CyberBot AI التعليمي
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {statCards.map((stat, index) => {
          const Icon = stat.icon
          return (
            <Card key={index} className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  {stat.title}
                </CardTitle>
                <div className={`w-10 h-10 ${stat.color} rounded-lg flex items-center justify-center`}>
                  <Icon className="w-5 h-5 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-gray-900 mb-1">
                  {stat.value.toLocaleString()}
                </div>
                <div className="flex items-center justify-between">
                  <p className="text-xs text-gray-500">
                    {stat.description}
                  </p>
                  <span className="text-xs text-green-600 font-medium">
                    {stat.trend}
                  </span>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <TrendingUp className="w-5 h-5" />
              <span>النشاط الأخير</span>
            </CardTitle>
            <CardDescription>
              آخر الأنشطة في النظام
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">مستخدم جديد انضم للنظام</p>
                  <p className="text-xs text-gray-500">منذ 5 دقائق</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">تم إكمال درس جديد</p>
                  <p className="text-xs text-gray-500">منذ 12 دقيقة</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">شراء اشتراك VIP</p>
                  <p className="text-xs text-gray-500">منذ 25 دقيقة</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">نشر خبر أمني جديد</p>
                  <p className="text-xs text-gray-500">منذ ساعة</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <DollarSign className="w-5 h-5" />
              <span>الإيرادات</span>
            </CardTitle>
            <CardDescription>
              إحصائيات المبيعات والإيرادات
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">إيرادات اليوم</span>
                <span className="font-bold text-green-600">$127.50</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">إيرادات الأسبوع</span>
                <span className="font-bold text-blue-600">$892.30</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">إيرادات الشهر</span>
                <span className="font-bold text-purple-600">$3,245.80</span>
              </div>
              <div className="pt-4 border-t">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">إجمالي الإيرادات</span>
                  <span className="text-lg font-bold text-gray-900">
                    ${stats?.shop?.revenue || 0}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default Dashboard

