import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { 
  Search, 
  Eye, 
  Plus, 
  Minus, 
  Crown,
  Calendar,
  Star
} from 'lucide-react'

const Users = () => {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 20,
    total: 0,
    pages: 0
  })
  const [selectedUser, setSelectedUser] = useState(null)
  const [userDetails, setUserDetails] = useState(null)
  const [pointsDialog, setPointsDialog] = useState(false)
  const [pointsForm, setPointsForm] = useState({
    points: '',
    reason: '',
    action: 'add'
  })

  useEffect(() => {
    fetchUsers()
  }, [pagination.page, search])

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const params = new URLSearchParams({
        page: pagination.page,
        limit: pagination.limit,
        search: search
      })

      const response = await fetch(`http://localhost:5001/api/admin/users?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      const data = await response.json()
      if (data.success) {
        setUsers(data.users)
        setPagination(prev => ({
          ...prev,
          total: data.pagination.total,
          pages: data.pagination.pages
        }))
      }
    } catch (error) {
      console.error('Error fetching users:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchUserDetails = async (userId) => {
    try {
      const token = localStorage.getItem('admin_token')
      const response = await fetch(`http://localhost:5001/api/admin/users/${userId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })

      const data = await response.json()
      if (data.success) {
        setUserDetails(data)
      }
    } catch (error) {
      console.error('Error fetching user details:', error)
    }
  }

  const updateUserPoints = async () => {
    try {
      const token = localStorage.getItem('admin_token')
      const response = await fetch(`http://localhost:5001/api/admin/users/${selectedUser}/points`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          points: parseInt(pointsForm.points),
          reason: pointsForm.reason,
          action: pointsForm.action
        }),
      })

      const data = await response.json()
      if (data.success) {
        setPointsDialog(false)
        setPointsForm({ points: '', reason: '', action: 'add' })
        fetchUsers()
        if (userDetails) {
          fetchUserDetails(selectedUser)
        }
      }
    } catch (error) {
      console.error('Error updating user points:', error)
    }
  }

  const handleSearch = (e) => {
    setSearch(e.target.value)
    setPagination(prev => ({ ...prev, page: 1 }))
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ar-SA')
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
          <h1 className="text-3xl font-bold text-gray-900">إدارة المستخدمين</h1>
          <p className="text-gray-500">إدارة حسابات المستخدمين ونقاطهم</p>
        </div>
      </div>

      {/* Search */}
      <Card>
        <CardHeader>
          <CardTitle>البحث والتصفية</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <Input
                placeholder="البحث بالاسم أو اسم المستخدم..."
                value={search}
                onChange={handleSearch}
                className="pl-10"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle>قائمة المستخدمين ({pagination.total})</CardTitle>
          <CardDescription>
            إجمالي المستخدمين المسجلين في النظام
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>المستخدم</TableHead>
                <TableHead>النقاط</TableHead>
                <TableHead>المستوى</TableHead>
                <TableHead>الحالة</TableHead>
                <TableHead>تاريخ التسجيل</TableHead>
                <TableHead>الإجراءات</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.user_id}>
                  <TableCell>
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-blue-600 font-medium">
                          {user.first_name?.charAt(0) || 'U'}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">
                          {user.first_name} {user.last_name}
                        </p>
                        <p className="text-sm text-gray-500">@{user.username}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Star className="w-4 h-4 text-yellow-500" />
                      <span className="font-medium">{user.points}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">
                      {user.level === 'beginner' ? 'مبتدئ' : 
                       user.level === 'intermediate' ? 'متوسط' : 'متقدم'}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    {user.is_vip ? (
                      <Badge className="bg-yellow-100 text-yellow-800">
                        <Crown className="w-3 h-3 mr-1" />
                        VIP
                      </Badge>
                    ) : (
                      <Badge variant="secondary">عادي</Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <span className="text-sm">{formatDate(user.registration_date)}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => {
                              setSelectedUser(user.user_id)
                              fetchUserDetails(user.user_id)
                            }}
                          >
                            <Eye className="w-4 h-4" />
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-2xl">
                          <DialogHeader>
                            <DialogTitle>تفاصيل المستخدم</DialogTitle>
                            <DialogDescription>
                              معلومات شاملة عن المستخدم ونشاطه
                            </DialogDescription>
                          </DialogHeader>
                          {userDetails && (
                            <div className="space-y-6">
                              {/* User Info */}
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <Label>الاسم الكامل</Label>
                                  <p className="text-sm text-gray-600">
                                    {userDetails.user.first_name} {userDetails.user.last_name}
                                  </p>
                                </div>
                                <div>
                                  <Label>اسم المستخدم</Label>
                                  <p className="text-sm text-gray-600">@{userDetails.user.username}</p>
                                </div>
                                <div>
                                  <Label>النقاط</Label>
                                  <p className="text-sm text-gray-600">{userDetails.user.points}</p>
                                </div>
                                <div>
                                  <Label>الدروس المكتملة</Label>
                                  <p className="text-sm text-gray-600">{userDetails.user.total_lessons_completed}</p>
                                </div>
                              </div>

                              {/* Points History */}
                              <div>
                                <Label>تاريخ النقاط</Label>
                                <div className="mt-2 space-y-2 max-h-32 overflow-y-auto">
                                  {userDetails.points_history.map((point, index) => (
                                    <div key={index} className="flex justify-between items-center text-sm">
                                      <span>{point.reason}</span>
                                      <span className={point.transaction_type === 'earned' ? 'text-green-600' : 'text-red-600'}>
                                        {point.transaction_type === 'earned' ? '+' : ''}{point.points}
                                      </span>
                                    </div>
                                  ))}
                                </div>
                              </div>

                              {/* Actions */}
                              <div className="flex space-x-2">
                                <Button 
                                  onClick={() => setPointsDialog(true)}
                                  className="flex-1"
                                >
                                  تعديل النقاط
                                </Button>
                              </div>
                            </div>
                          )}
                        </DialogContent>
                      </Dialog>
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

      {/* Points Dialog */}
      <Dialog open={pointsDialog} onOpenChange={setPointsDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>تعديل النقاط</DialogTitle>
            <DialogDescription>
              إضافة أو خصم نقاط من حساب المستخدم
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>عدد النقاط</Label>
              <Input
                type="number"
                value={pointsForm.points}
                onChange={(e) => setPointsForm(prev => ({ ...prev, points: e.target.value }))}
                placeholder="أدخل عدد النقاط"
              />
            </div>
            <div>
              <Label>السبب</Label>
              <Input
                value={pointsForm.reason}
                onChange={(e) => setPointsForm(prev => ({ ...prev, reason: e.target.value }))}
                placeholder="سبب التعديل"
              />
            </div>
            <div className="flex space-x-2">
              <Button
                variant={pointsForm.action === 'add' ? 'default' : 'outline'}
                onClick={() => setPointsForm(prev => ({ ...prev, action: 'add' }))}
                className="flex-1"
              >
                <Plus className="w-4 h-4 mr-2" />
                إضافة
              </Button>
              <Button
                variant={pointsForm.action === 'subtract' ? 'default' : 'outline'}
                onClick={() => setPointsForm(prev => ({ ...prev, action: 'subtract' }))}
                className="flex-1"
              >
                <Minus className="w-4 h-4 mr-2" />
                خصم
              </Button>
            </div>
            <Button onClick={updateUserPoints} className="w-full">
              تطبيق التغيير
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default Users

