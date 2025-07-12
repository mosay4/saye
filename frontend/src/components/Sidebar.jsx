import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Users, 
  BookOpen, 
  Newspaper, 
  ShoppingCart, 
  Settings,
  Shield
} from 'lucide-react'

const Sidebar = () => {
  const location = useLocation()

  const menuItems = [
    {
      path: '/dashboard',
      icon: LayoutDashboard,
      label: 'لوحة التحكم',
      active: location.pathname === '/dashboard' || location.pathname === '/'
    },
    {
      path: '/users',
      icon: Users,
      label: 'المستخدمين',
      active: location.pathname === '/users'
    },
    {
      path: '/lessons',
      icon: BookOpen,
      label: 'الدروس',
      active: location.pathname === '/lessons'
    },
    {
      path: '/news',
      icon: Newspaper,
      label: 'الأخبار',
      active: location.pathname === '/news'
    },
    {
      path: '/shop',
      icon: ShoppingCart,
      label: 'المتجر',
      active: location.pathname === '/shop'
    },
    {
      path: '/settings',
      icon: Settings,
      label: 'الإعدادات',
      active: location.pathname === '/settings'
    }
  ]

  return (
    <div className="w-64 bg-white shadow-lg border-r border-gray-200">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">CyberBot AI</h1>
            <p className="text-sm text-gray-500">لوحة التحكم</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            return (
              <li key={item.path}>
                <Link
                  to={item.path}
                  className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                    item.active
                      ? 'bg-blue-50 text-blue-700 border-r-4 border-blue-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${item.active ? 'text-blue-700' : 'text-gray-400'}`} />
                  <span className="font-medium">{item.label}</span>
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
        <div className="text-center">
          <p className="text-xs text-gray-500">
            CyberBot AI v1.0
          </p>
          <p className="text-xs text-gray-400">
            © 2024 جميع الحقوق محفوظة
          </p>
        </div>
      </div>
    </div>
  )
}

export default Sidebar

