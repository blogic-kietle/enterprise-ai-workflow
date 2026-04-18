# SKILL.md Template for .agent/ Folder

Đây là template cho file `SKILL.md` trong thư mục `.agent/` của mỗi project. File này mô tả các kỹ năng đặc thù, tools, và workflows cụ thể của dự án này.

---

```markdown
# Project Skills & Tools

**Project Name**: [Tên dự án]  
**Repository**: [URL GitHub]  
**Tech Stack**: [Ví dụ: Angular 18, TypeScript, RxJS, TailwindCSS]  
**Last Updated**: [Ngày cập nhật]

## 1. Project-Specific Tools & Libraries

Liệt kê các tools, libraries, hoặc services đặc thù mà dự án này sử dụng:

### 1.1. Frontend Libraries
- **State Management**: [Ví dụ: NgRx, Akita, hay chỉ RxJS]
- **HTTP Client**: [Ví dụ: HttpClient, Axios]
- **UI Framework**: [Ví dụ: Angular Material, PrimeNG, TailwindCSS]
- **Testing**: [Ví dụ: Jasmine, Jest, Cypress]

### 1.2. Backend Integration
- **API Base URL**: [Ví dụ: https://api.example.com/v1]
- **Authentication**: [Ví dụ: JWT, OAuth2]
- **Key Endpoints**: 
  - `GET /api/v1/users` - Lấy danh sách users
  - `POST /api/v1/users` - Tạo user mới

### 1.3. DevOps & CI/CD
- **Build Tool**: [Ví dụ: Webpack, Vite, Angular CLI]
- **CI/CD Platform**: [Ví dụ: Jenkins, GitHub Actions]
- **Deployment Target**: [Ví dụ: Docker, Kubernetes, AWS S3]
- **Environment Variables**: [Ví dụ: API_URL, AUTH_TOKEN]

## 2. Custom Patterns & Conventions

Mô tả các pattern hoặc convention độc quyền của dự án này:

### 2.1. Naming Conventions
- **Services**: `*Service.ts` (Ví dụ: `UserService.ts`)
- **Components**: `*Component.ts` (Ví dụ: `UserListComponent.ts`)
- **Models**: `*.model.ts` (Ví dụ: `User.model.ts`)
- **Custom Pattern**: [Nếu có pattern đặc biệt nào khác]

### 2.2. Folder Structure Specifics
```
src/
├── app/
│   ├── core/
│   │   ├── services/
│   │   │   ├── auth.service.ts
│   │   │   └── api.service.ts
│   │   └── interceptors/
│   ├── shared/
│   │   ├── components/
│   │   ├── pipes/
│   │   └── directives/
│   └── features/
│       ├── [feature-name]/
│       │   ├── pages/
│       │   ├── components/
│       │   ├── services/
│       │   └── models/
```

### 2.3. Code Style Specifics
- **Indentation**: [Ví dụ: 2 spaces, 4 spaces, tabs]
- **Line Length**: [Ví dụ: 100 characters, 120 characters]
- **Quote Style**: [Ví dụ: Single quotes, double quotes]
- **Semicolons**: [Ví dụ: Always, never]

## 3. Common Tasks & Workflows

Mô tả các task thường xuyên và cách thực hiện chúng:

### 3.1. Creating a New Feature Module
**Steps**:
1. Tạo thư mục `src/app/features/[feature-name]`
2. Tạo `[feature-name].module.ts`
3. Tạo `pages/` subfolder cho routed components
4. Tạo `components/` subfolder cho dumb components
5. Tạo `services/` subfolder cho feature-specific services
6. Tạo `models/` subfolder cho interfaces/types

**Template Command**: 
```bash
ng generate module features/[feature-name] --routing
```

### 3.2. Creating a Smart Component
**Pattern**: 
- Handles data fetching from services
- Uses RxJS observables with async pipe
- Delegates UI rendering to dumb components

**Template**:
```typescript
@Component({
  selector: 'app-[feature]-page',
  template: `
    <app-[feature]-list
      [items]="items$ | async"
      (itemSelected)="onItemSelected($event)"
    ></app-[feature]-list>
  `
})
export class [Feature]PageComponent implements OnInit {
  items$ = this.service.getItems();
  
  constructor(private service: [Feature]Service) {}
  
  onItemSelected(item: any) {
    // Handle selection
  }
}
```

### 3.3. Creating a Dumb Component
**Pattern**:
- Receives data via @Input()
- Emits events via @Output()
- Uses ChangeDetectionStrategy.OnPush

**Template**:
```typescript
@Component({
  selector: 'app-[feature]-list',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `...`
})
export class [Feature]ListComponent {
  @Input() items: any[] = [];
  @Output() itemSelected = new EventEmitter<any>();
  
  onSelect(item: any) {
    this.itemSelected.emit(item);
  }
}
```

### 3.4. Running Tests
**Command**: 
```bash
npm run test
# hoặc
ng test
```

**Coverage**: Mục tiêu là 80%+ code coverage

### 3.5. Building for Production
**Command**: 
```bash
npm run build
# hoặc
ng build --configuration production
```

## 4. Known Issues & Workarounds

Liệt kê các vấn đề đã biết và cách giải quyết:

### 4.1. Issue: [Mô tả vấn đề]
**Workaround**: [Cách giải quyết]

### 4.2. Issue: [Mô tả vấn đề]
**Workaround**: [Cách giải quyết]

## 5. Integration Points

Mô tả các điểm tích hợp với các hệ thống khác:

### 5.1. Jenkins Integration
- **Jenkinsfile Location**: `./Jenkinsfile`
- **Build Stage**: Chạy `npm install && npm run build`
- **Test Stage**: Chạy `npm run test`
- **Deploy Stage**: Push image Docker lên registry

### 5.2. API Integration
- **Base URL**: [Ví dụ: https://api.example.com]
- **Authentication Header**: `Authorization: Bearer {token}`
- **Error Handling**: [Ví dụ: Global error interceptor]

### 5.3. Database Integration (nếu có)
- **ORM/Query Builder**: [Ví dụ: TypeORM, Prisma]
- **Connection String**: [Ví dụ: mongodb://localhost:27017/db]

## 6. Performance Considerations

Các lưu ý về hiệu năng của dự án:

- **Change Detection**: Sử dụng OnPush strategy cho tất cả dumb components
- **Lazy Loading**: Các feature modules phải được lazy load
- **Bundle Size**: Mục tiêu < 500KB (gzipped)
- **Image Optimization**: Tất cả images phải được tối ưu hóa

## 7. Security Considerations

Các lưu ý bảo mật:

- **Secrets Management**: Không commit API keys, tokens vào Git
- **CORS**: Cấu hình CORS đúng cho các domain được phép
- **XSS Protection**: Sử dụng Angular's built-in sanitization
- **CSRF Protection**: Sử dụng CSRF tokens nếu backend yêu cầu

## 8. Quick Reference

Các lệnh thường dùng:

```bash
# Install dependencies
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build

# Lint code
npm run lint

# Format code
npm run format
```

---

**Note**: File này được đọc bởi AI Agent trước khi thực thi bất kỳ task nào. Hãy giữ nó cập nhật!
```
