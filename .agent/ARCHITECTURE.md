# ARCHITECTURE.md Template for .agent/ Folder

Đây là template cho file `ARCHITECTURE.md` trong thư mục `.agent/` của mỗi project. File này mô tả kiến trúc tổng thể của dự án.

---

```markdown
# Project Architecture

**Project Name**: [Tên dự án]  
**Tech Stack**: [Ví dụ: Angular 18 + TypeScript + RxJS]  
**Architecture Pattern**: [Ví dụ: Feature-based modular architecture]  
**Last Updated**: [Ngày cập nhật]

## 1. High-Level Architecture Overview

Mô tả tổng quan về kiến trúc của dự án:

### 1.1. System Diagram
```
┌─────────────────────────────────────────┐
│         Angular Frontend App            │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐   │
│  │    Feature Modules              │   │
│  │  (Users, Products, Dashboard)   │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │    Shared Components/Services   │   │
│  │  (UI, Utilities, Interceptors)  │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
              ↓
    ┌─────────────────────────┐
    │   Backend API Server    │
    │ (REST/GraphQL)          │
    └─────────────────────────┘
              ↓
    ┌─────────────────────────┐
    │   Database              │
    │ (MongoDB/PostgreSQL)    │
    └─────────────────────────┘
```

### 1.2. Technology Stack
| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend Framework | Angular 18+ | Main UI framework |
| Language | TypeScript | Type-safe development |
| State Management | [RxJS/NgRx/Akita] | Manage application state |
| HTTP Client | HttpClient | API communication |
| UI Components | [Material/PrimeNG/Custom] | UI elements |
| Styling | [TailwindCSS/SCSS] | Styling |
| Testing | [Jasmine/Jest/Cypress] | Automated testing |
| Build Tool | Angular CLI/Webpack | Build and bundling |

## 2. Folder Structure & Organization

Mô tả cấu trúc thư mục chi tiết:

```
src/
├── app/
│   ├── core/                          # Singleton services, guards, interceptors
│   │   ├── services/
│   │   │   ├── auth.service.ts
│   │   │   ├── api.service.ts
│   │   │   └── error.service.ts
│   │   ├── guards/
│   │   │   └── auth.guard.ts
│   │   ├── interceptors/
│   │   │   └── error.interceptor.ts
│   │   └── models/
│   │       └── user.model.ts
│   │
│   ├── shared/                        # Reusable components, pipes, directives
│   │   ├── components/
│   │   │   ├── header/
│   │   │   ├── footer/
│   │   │   ├── sidebar/
│   │   │   └── common-ui/
│   │   ├── pipes/
│   │   │   └── custom.pipe.ts
│   │   ├── directives/
│   │   │   └── custom.directive.ts
│   │   └── utils/
│   │       └── helpers.ts
│   │
│   ├── features/                      # Feature modules
│   │   ├── users/
│   │   │   ├── pages/
│   │   │   │   ├── user-list-page.component.ts
│   │   │   │   └── user-detail-page.component.ts
│   │   │   ├── components/
│   │   │   │   ├── user-card.component.ts
│   │   │   │   └── user-form.component.ts
│   │   │   ├── services/
│   │   │   │   └── user.service.ts
│   │   │   ├── models/
│   │   │   │   └── user.model.ts
│   │   │   └── users.module.ts
│   │   │
│   │   ├── products/
│   │   │   └── [Similar structure]
│   │   │
│   │   └── dashboard/
│   │       └── [Similar structure]
│   │
│   ├── layout/
│   │   └── main-layout.component.ts
│   │
│   ├── app.component.ts
│   ├── app.module.ts
│   └── app-routing.module.ts
│
├── assets/
│   ├── images/
│   ├── icons/
│   └── styles/
│
├── environments/
│   ├── environment.ts
│   └── environment.prod.ts
│
└── main.ts
```

### 2.1. Core Module
**Purpose**: Chứa các singleton services, guards, interceptors chỉ import vào AppModule.

**Files**:
- `auth.service.ts`: Quản lý authentication
- `api.service.ts`: Base API service
- `error.service.ts`: Xử lý lỗi global
- `auth.guard.ts`: Route guard cho protected routes

### 2.2. Shared Module
**Purpose**: Chứa các components, pipes, directives có thể tái sử dụng trong bất kỳ feature module nào.

**Files**:
- `header.component.ts`: Header chung
- `footer.component.ts`: Footer chung
- `custom.pipe.ts`: Custom pipes
- `helpers.ts`: Utility functions

### 2.3. Features
**Purpose**: Chứa các feature modules độc lập, mỗi feature có cấu trúc riêng.

**Quy tắc**:
- Mỗi feature là một module riêng
- Feature có thể lazy load
- Feature không được import từ feature khác (chỉ import từ shared/core)

## 3. Component Architecture

Mô tả kiến trúc component của dự án:

### 3.1. Smart vs Dumb Components

**Smart Components (Container/Page Components)**:
- Nằm trong thư mục `pages/`
- Quản lý state và logic nghiệp vụ
- Gọi services để lấy/cập nhật dữ liệu
- Truyền dữ liệu xuống Dumb Components
- Lắng nghe events từ Dumb Components

**Dumb Components (Presentational Components)**:
- Nằm trong thư mục `components/`
- Chỉ nhận dữ liệu qua @Input()
- Phát events qua @Output()
- Không gọi services
- Sử dụng ChangeDetectionStrategy.OnPush

### 3.2. Component Lifecycle
```
1. Component Created
   ↓
2. ngOnInit() - Khởi tạo, lấy dữ liệu
   ↓
3. ngAfterViewInit() - Template đã render
   ↓
4. ngOnDestroy() - Cleanup, unsubscribe
```

### 3.3. Change Detection Strategy
- **Default**: OnPush cho tất cả Dumb Components
- **Rationale**: Tối ưu performance, giảm re-render không cần thiết

## 4. State Management

Mô tả cách quản lý state trong dự án:

### 4.1. Local Component State
- Sử dụng RxJS Subjects/BehaviorSubjects
- Unsubscribe trong ngOnDestroy

### 4.2. Feature-Level State (nếu sử dụng NgRx)
- Mỗi feature có store riêng
- Actions, Reducers, Effects tổ chức trong feature folder

### 4.3. Global State (nếu có)
- Authentication state
- User preferences
- Global notifications

## 5. Data Flow & Communication

Mô tả luồng dữ liệu trong ứng dụng:

### 5.1. HTTP Communication
```
Component
   ↓
Service (calls API)
   ↓
HttpClient (with Interceptors)
   ↓
Backend API
```

### 5.2. Error Handling
- Global Error Interceptor xử lý HTTP errors
- Hiển thị error message cho user
- Log errors cho debugging

### 5.3. Authentication Flow
```
Login Component
   ↓
Auth Service (calls /login API)
   ↓
Store token in localStorage
   ↓
Add token to HTTP headers (Interceptor)
   ↓
Redirect to dashboard
```

## 6. Routing Architecture

Mô tả cấu trúc routing:

### 6.1. Main Routes
```typescript
const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  { path: 'dashboard', component: DashboardPageComponent },
  { path: 'users', loadChildren: () => import('./features/users/users.module').then(m => m.UsersModule) },
  { path: 'products', loadChildren: () => import('./features/products/products.module').then(m => m.ProductsModule) },
  { path: '**', component: NotFoundComponent }
];
```

### 6.2. Feature Routes
```typescript
// users.module.ts
const routes: Routes = [
  {
    path: '',
    component: UsersLayoutComponent,
    children: [
      { path: '', component: UserListPageComponent },
      { path: ':id', component: UserDetailPageComponent }
    ]
  }
];
```

### 6.3. Route Guards
- `AuthGuard`: Kiểm tra authentication trước khi vào route
- `PermissionGuard`: Kiểm tra quyền trước khi vào route

## 7. Service Architecture

Mô tả cấu trúc services:

### 7.1. API Service
- Base service cho tất cả HTTP calls
- Xử lý common headers, error handling
- Định nghĩa base URL

### 7.2. Feature Services
- Mỗi feature có service riêng
- Gọi API Service để lấy dữ liệu
- Xử lý business logic

### 7.3. Utility Services
- Authentication Service
- Notification Service
- Storage Service

## 8. Module Organization

Mô tả cách organize modules:

### 8.1. AppModule
- Import CoreModule (một lần duy nhất)
- Import SharedModule
- Declare AppComponent
- Bootstrap AppComponent

### 8.2. Feature Modules
- Declare components, pipes, directives của feature
- Import SharedModule nếu cần
- Có routing module riêng

### 8.3. Shared Module
- Declare reusable components, pipes, directives
- Export chúng để các module khác sử dụng
- Không declare services (services nên ở Core)

## 9. Performance Optimization

Các kỹ thuật tối ưu performance:

### 9.1. Lazy Loading
- Feature modules được lazy load
- Giảm bundle size của main chunk

### 9.2. Change Detection
- OnPush strategy cho dumb components
- Giảm số lần change detection chạy

### 9.3. Unsubscribe Pattern
```typescript
private destroy$ = new Subject<void>();

ngOnInit() {
  this.service.getData()
    .pipe(takeUntil(this.destroy$))
    .subscribe(data => this.data = data);
}

ngOnDestroy() {
  this.destroy$.next();
  this.destroy$.complete();
}
```

### 9.4. TrackBy in *ngFor
```html
<div *ngFor="let item of items; trackBy: trackByFn">
  {{ item.name }}
</div>
```

## 10. Testing Strategy

Mô tả cách test trong dự án:

### 10.1. Unit Tests
- Test services với mock data
- Test components với test fixtures
- Mục tiêu: 80%+ coverage

### 10.2. Integration Tests
- Test feature workflows
- Test API integration

### 10.3. E2E Tests
- Test critical user flows
- Test with real browser (Cypress)

## 11. Build & Deployment

Mô tả quy trình build và deployment:

### 11.1. Development Build
```bash
ng serve
```

### 11.2. Production Build
```bash
ng build --configuration production
```

### 11.3. Docker Deployment
- Multi-stage Dockerfile
- Build stage: Node.js để build Angular app
- Runtime stage: Nginx để serve static files

### 11.4. CI/CD Pipeline
- Jenkins triggers on git push
- Runs linting, tests, build
- Deploys to staging/production

---

**Note**: File này được đọc bởi AI Agent trước khi thực thi bất kỳ task nào. Hãy giữ nó cập nhật!
```
