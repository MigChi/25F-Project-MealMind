CREATE DATABASE IF NOT EXISTS mealmind;
USE mealmind;

DROP TABLE IF EXISTS SystemAlert;
DROP TABLE IF EXISTS MetricSnapshot;
DROP TABLE IF EXISTS SystemMetric;
DROP TABLE IF EXISTS RecipeUsageStatistic;
DROP TABLE IF EXISTS MealPlanEntry;
DROP TABLE IF EXISTS MealPlan;
DROP TABLE IF EXISTS FavoriteRecipe;
DROP TABLE IF EXISTS UsersBudgetProfile;
DROP TABLE IF EXISTS UserBudgetProfile;
DROP TABLE IF EXISTS InventoryItem;
DROP TABLE IF EXISTS WasteStatistic;
DROP TABLE IF EXISTS RecipeIngredient;
DROP TABLE IF EXISTS DemographicSegment;
DROP TABLE IF EXISTS TimePeriod;
DROP TABLE IF EXISTS Ingredient;
DROP TABLE IF EXISTS Category;
DROP TABLE IF EXISTS User;
DROP TABLE IF EXISTS Recipe;

CREATE TABLE IF NOT EXISTS Category
(
    CategoryID   int          not null
        primary key,
    CategoryName varchar(255) null
);

CREATE TABLE IF NOT EXISTS DemographicSegment
(
    SegmentID int          not null
        primary key,
    Name      varchar(255) null,
    AgeMin    int          null,
    AgeMax    int          null,
    Region    varchar(255) null
);

CREATE TABLE IF NOT EXISTS Ingredient
(
    IngredientID int not null
        primary key,
    CategoryID   int null,
    constraint Ingredient_ibfk_1
        foreign key (CategoryID) references Category (CategoryID)
);

create index CategoryID
    on Ingredient (CategoryID);

CREATE TABLE IF NOT EXISTS Recipe
(
    RecipeId        int          not null
        primary key,
    Name            varchar(255) null,
    PrepTimeMinutes varchar(255) null,
    DifficultyLevel varchar(255) null,
    Instructions    text         null,
    Status          varchar(255) null,
    CreatedAt       datetime     null,
    LastUpdateAt    datetime     null
);

CREATE TABLE IF NOT EXISTS RecipeIngredient
(
    RecipeID         int            not null,
    IngredientID     int            not null,
    RequiredQuantity decimal(10, 2) null,
    Unit             varchar(255)   null,
    primary key (RecipeID, IngredientID),
    constraint RecipeIngredient_ibfk_1
        foreign key (IngredientID) references Ingredient (IngredientID),
    constraint RecipeIngredient_ibfk_2
        foreign key (RecipeID) references Recipe (RecipeId)
);

create index IngredientID
    on RecipeIngredient (IngredientID);

CREATE TABLE IF NOT EXISTS SystemMetric
(
    MetricID    int          not null
        primary key,
    Name        varchar(255) null,
    Description text         null
);

CREATE TABLE IF NOT EXISTS MetricSnapshot
(
    SnapshotID int            not null
        primary key,
    MetricID   int            null,
    MeasuredAt datetime       null,
    Value      decimal(10, 2) null,
    constraint MetricSnapshot_ibfk_1
        foreign key (MetricID) references SystemMetric (MetricID)
);

create index MetricID
    on MetricSnapshot (MetricID);

CREATE TABLE IF NOT EXISTS SystemAlert
(
    AlertID    int          not null
        primary key,
    MetricID   int          null,
    AlertType  varchar(255) null,
    Severity   varchar(255) null,
    Message    text         null,
    CreatedAt  datetime     null,
    ResolvedAt datetime     null,
    Status     varchar(255) null,
    constraint SystemAlert_ibfk_1
        foreign key (MetricID) references SystemMetric (MetricID)
);

create index MetricID
    on SystemAlert (MetricID);

CREATE TABLE IF NOT EXISTS TimePeriod
(
    PeriodID    int          not null
        primary key,
    StartDate   date         null,
    EndDate     date         null,
    Granularity varchar(255) null
);

CREATE TABLE IF NOT EXISTS RecipeUsageStatistic
(
    UsageStatID int not null
        primary key,
    RecipeID    int null,
    PeriodID    int null,
    SegmentID   int null,
    UsageCount  int null,
    UniqueUsers int null,
    constraint RecipeUsageStatistic_ibfk_1
        foreign key (RecipeID) references Recipe (RecipeId),
    constraint RecipeUsageStatistic_ibfk_2
        foreign key (PeriodID) references TimePeriod (PeriodID),
    constraint RecipeUsageStatistic_ibfk_3
        foreign key (SegmentID) references DemographicSegment (SegmentID)
);

create index PeriodID
    on RecipeUsageStatistic (PeriodID);

create index RecipeID
    on RecipeUsageStatistic (RecipeID);

create index SegmentID
    on RecipeUsageStatistic (SegmentID);

CREATE TABLE IF NOT EXISTS User
(
    UserID int          not null
        primary key,
    Email  varchar(255) null,
    Region varchar(255) null,
    FName  varchar(255) null,
    LName  varchar(255) null,
    Age    int          null
);

CREATE TABLE IF NOT EXISTS FavoriteRecipe
(
    UserID        int  not null,
    RecipeID      int  not null,
    FavoritedDate date null,
    primary key (UserID, RecipeID),
    constraint FavoriteRecipe_ibfk_1
        foreign key (UserID) references User (UserID),
    constraint FavoriteRecipe_ibfk_2
        foreign key (RecipeID) references Recipe (RecipeId)
);

create index RecipeID
    on FavoriteRecipe (RecipeID);

CREATE TABLE IF NOT EXISTS InventoryItem
(
    UserID         int            not null,
    IngredientID   int            not null,
    AddedDate      date           not null,
    Quantity       decimal(10, 2) null,
    Unit           varchar(255)   null,
    ExpirationDate date           null,
    Status         varchar(255)   null,
    primary key (UserID, IngredientID, AddedDate),
    constraint InventoryItem_ibfk_1
        foreign key (UserID) references User (UserID),
    constraint InventoryItem_ibfk_2
        foreign key (IngredientID) references Ingredient (IngredientID)
);

create index IngredientID
    on InventoryItem (IngredientID);

CREATE TABLE IF NOT EXISTS MealPlan
(
    MealPlanID int        not null
        primary key,
    UserID     int        null,
    StartDate  date       null,
    EndDate    date       null,
    IsSaved    tinyint(1) null,
    constraint MealPlan_ibfk_1
        foreign key (UserID) references User (UserID)
);

create index UserID
    on MealPlan (UserID);

CREATE TABLE IF NOT EXISTS MealPlanEntry
(
    MealPlanID int          not null,
    Date       date         not null,
    MealType   varchar(255) not null,
    RecipeID   int          null,
    Notes      text         null,
    primary key (MealPlanID, Date, MealType),
    constraint MealPlanEntry_ibfk_1
        foreign key (MealPlanID) references MealPlan (MealPlanID),
    constraint MealPlanEntry_ibfk_2
        foreign key (RecipeID) references Recipe (RecipeId)
);

create index RecipeID
    on MealPlanEntry (RecipeID);

CREATE TABLE IF NOT EXISTS UserBudgetProfile
(
    UserID             int            not null
        primary key,
    WeeklyBudgetAmount decimal(10, 2) null,
    Currency           varchar(255)   null,
    constraint UserBudgetProfile_ibfk_1
        foreign key (UserID) references User (UserID)
);

CREATE TABLE IF NOT EXISTS UsersBudgetProfile
(
    UserID    int          not null
        primary key,
    DietTypes varchar(255) null,
    Notes     text         null,
    constraint UsersBudgetProfile_ibfk_1
        foreign key (UserID) references User (UserID)
);

CREATE TABLE IF NOT EXISTS WasteStatistic
(
    WasteStatID      int            not null
        primary key,
    IngredientID     int            null,
    PeriodID         int            null,
    SegmentID        int            null,
    WastedAmount     decimal(10, 2) null,
    WasteRatePercent decimal(5, 2)  null,
    constraint WasteStatistic_ibfk_1
        foreign key (IngredientID) references Ingredient (IngredientID),
    constraint WasteStatistic_ibfk_2
        foreign key (PeriodID) references TimePeriod (PeriodID),
    constraint WasteStatistic_ibfk_3
        foreign key (SegmentID) references DemographicSegment (SegmentID)
);

create index IngredientID
    on WasteStatistic (IngredientID);

create index PeriodID
    on WasteStatistic (PeriodID);

create index SegmentID
    on WasteStatistic (SegmentID);

