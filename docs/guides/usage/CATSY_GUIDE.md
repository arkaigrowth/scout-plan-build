# Catsy Developer Guide

**Practical examples for using the development accelerator with Catsy's Java codebase.**

## Table of Contents
1. [Common Tasks](#common-tasks)
2. [Catsy-Specific Patterns](#catsy-specific-patterns)
3. [Real Examples](#real-examples)
4. [Integration with Our Stack](#integration-with-our-stack)

## Common Tasks

### 1. Add a New Product Attribute

```bash
# The tool understands our Product model
/plan_w_docs "Add 'sustainability_score' attribute to Product entity with validation range 0-100" \
  "catsy-product-model.json"

# Generates:
# - JPA entity update
# - Migration script
# - DTO changes
# - Validation rules
# - Test coverage
```

### 2. Build Integration Channel Connector

```bash
/plan_w_docs "Create Shopify integration connector following our channel framework" \
  "catsy-integration-patterns.json"

# Generates:
# - Channel adapter implementation
# - Webhook handlers
# - Product sync logic
# - Error handling
# - Integration tests
```

### 3. Fix Performance Issues

```bash
/plan_w_docs "Optimize ProductSearchService N+1 query issues" \
  "performance-logs.txt"

# Generates:
# - JPA query optimization
# - Fetch strategies
# - Caching configuration
# - Performance tests
```

### 4. Modernize Legacy Code

```bash
/plan_w_docs "Refactor LegacyProductManager to use Spring DI and modern patterns" \
  "legacy-code.java"

# Generates:
# - Service/Repository split
# - Dependency injection
# - Transaction management
# - Comprehensive tests
```

## Catsy-Specific Patterns

### Our Stack
- **Framework**: Spring Boot 3.2
- **Build**: Maven
- **Database**: PostgreSQL + JPA/Hibernate
- **Testing**: JUnit 5 + Mockito
- **API**: REST + OpenAPI

### Our Conventions

The tool knows our patterns:

```java
// It generates controllers like we write them
@RestController
@RequestMapping("/api/v1/products")
@Tag(name = "Products", description = "Product management operations")
public class ProductController {

    @Operation(summary = "Create product")
    @PostMapping
    public ResponseEntity<ProductDTO> createProduct(
        @Valid @RequestBody CreateProductRequest request) {
        // Follows our response pattern
        return ResponseEntity.ok(
            ProductResponse.success(productService.create(request))
        );
    }
}
```

## Real Examples

### Example 1: Product Variant System

**Task**: "Add variant management to products (size, color, SKU)"

**Generated** (15 minutes):
```java
// Entity changes
@Entity
public class Product {
    @OneToMany(cascade = CascadeType.ALL, mappedBy = "product")
    private Set<ProductVariant> variants = new HashSet<>();
}

@Entity
public class ProductVariant {
    @Id
    private String sku;

    @ManyToOne
    @JoinColumn(name = "product_id")
    private Product product;

    @ElementCollection
    @CollectionTable(name = "variant_attributes")
    private Map<String, String> attributes;

    // Inventory, pricing, etc.
}

// Repository with optimized queries
@Query("SELECT p FROM Product p LEFT JOIN FETCH p.variants WHERE p.id = :id")
Optional<Product> findByIdWithVariants(@Param("id") Long id);

// Complete service layer
// Full test coverage
// Migration scripts
```

### Example 2: Async Job Processing

**Task**: "Add async product import job with progress tracking"

**Generated** (20 minutes):
- Spring Batch configuration
- Job/Step definitions
- Progress tracking via websockets
- Error handling and retry logic
- Admin UI components
- Integration tests

### Example 3: Multi-tenant Support

**Task**: "Add tenant isolation for product catalog"

**Generated** (30 minutes):
- Hibernate filters
- Tenant context management
- Request interceptors
- Test fixtures for multi-tenant scenarios
- Performance considerations

## Integration with Our Stack

### Works With Our CI/CD

```yaml
# Generated code passes our pipeline
- mvn clean test  # ✅ Tests pass
- mvn sonar:sonar # ✅ Quality gates pass
- mvn verify      # ✅ Coverage > 80%
```

### Follows Our API Standards

```java
// Generates OpenAPI-compliant endpoints
@Operation(
    summary = "Search products",
    description = "Search products with filtering and pagination"
)
@ApiResponses({
    @ApiResponse(responseCode = "200", description = "Success"),
    @ApiResponse(responseCode = "400", description = "Invalid parameters")
})
@GetMapping("/search")
public Page<ProductDTO> search(
    @Parameter(description = "Search query") @RequestParam String q,
    @Parameter(hidden = true) Pageable pageable
) {
    // Implementation following our patterns
}
```

### Integrates with Our Services

The tool understands our service boundaries:

```java
// Knows to use our existing services
@Autowired private AuthenticationService authService;
@Autowired private NotificationService notificationService;
@Autowired private AuditService auditService;

// Generates proper service integration
public ProductDTO createProduct(CreateProductRequest request) {
    // Uses our auth
    User user = authService.getCurrentUser();

    // Our audit pattern
    auditService.log(AuditAction.PRODUCT_CREATE, user, request);

    // Our notification pattern
    notificationService.notify(new ProductCreatedEvent(product));

    return mapper.toDTO(product);
}
```

## Tips for Best Results

### 1. Include Context
```bash
# Good - includes our patterns
/plan_w_docs "Add feature" "our-patterns.json"

# Better - includes specific examples
/plan_w_docs "Add feature like XYZ" "xyz-implementation.java"
```

### 2. Reference Our Docs
```bash
# Include our API docs
/plan_w_docs "Create endpoint" "https://api.catsy.com/docs"
```

### 3. Use Our Terminology
- "Channel" not "Integration"
- "Attribute" not "Property"
- "Variant" not "Option"

## Limitations

**What it WON'T do**:
- Deploy to production
- Make database changes directly
- Commit without review
- Handle Catsy-specific business logic perfectly

**What it WILL do**:
- Generate 80-90% correct code
- Follow our patterns
- Create comprehensive tests
- Save hours of boilerplate

## Getting Help

1. **Not working?** Check [TECHNICAL_REFERENCE.md](TECHNICAL_REFERENCE.md)
2. **Wrong patterns?** Update context files in `catsy-context/`
3. **Need support?** Slack #dev-automation

---

*Remember: This tool generates code for review, not for blind deployment. Always review, test, and understand what's generated.*