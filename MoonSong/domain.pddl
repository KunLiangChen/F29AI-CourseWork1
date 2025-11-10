(define (domain lunar)
    (:requirements :strips :typing)

    ; -------------------------------
    ; Types
    ; -------------------------------

    ; EXAMPLE

    ; (:types
    ;     parent_type
    ;     child_type - parent_type

    ; )
    (:types
        equipment
        rover - equipment
        lander - equipment
        location
        data
        scan - data
        image - data
        sample
    )

    ; -------------------------------
    ; Predicates
    ; -------------------------------

    ; EXAMPLE

    ; (:predicates
    ;     (no_arity_predicate)
    ;     (one_arity_predicate ?p - parameter_type)
    ; )

    (:predicates
        (is_landed ?lan - lander) ;If not then lander can choose a location to land
        (on_postion ?e - equipment ?l - location) ; equipment is on a location
        (is_connectd ?l1 - location ?l2 - location) ; two locations are connected
        (has_picture ?l - location ?i - image) ; location has picture
        (has_sample ?l - location ?s - sample);This location has a sample
        (has_scan ?l - location ?sc - scan);This location has a scan
        (data_captured ?d - data) ; data is captured
        (empty_memory ?r - rover);Rover is full, we can't hold more data
        (hand_empty ?r - rover)
        (sample_collected ?s - sample)
        (is_full ?lan - lander) ;lander is full of sample
        (has_received ?d - data)
        (has_received ?s - sample)
        
    )

    ; -------------------------------
    ; Actions
    ; -------------------------------

    ; EXAMPLE

    ; (:action action-template
    ;     :parameters (?p - parameter_type)
    ;     :precondition (and
    ;         (one_arity_predicate ?p)
    ;     )
    ;     :effect 
    ;     (and 
    ;         (no_arity_predicate)
    ;         (not (one_arity_predicate ?p))
    ;     )
    ; )

    (:action rover_land 
        :parameters (?lan - lander ?r - rover ?l - location)
        :precondition 
        (and
            (not (is_landed ?lan))
            )
        :effect 
        (and
            (is_landed ?lan)
            (on_postion ?lan ?l)
            (on_postion ?r ?l)
        )
    )
    
    (:action rover_move
        :parameters (?l1 - location ?l2 - location ?r - rover)
        :precondition
        (and
            (not (on_postion ?r ?l2))
            (on_postion ?r ?l1)
            (is_connectd ?l1 ?l2)
        )
        :effect
        (and
            (not (on_postion ?r ?l1))
            (on_postion ?r ?l2)
        )
    )
    
    (:action take_picture
        :parameters (?r - rover ?l - location ?i - image)
        :precondition
        (and
            (on_postion ?r ?l)
            (has_picture ?l)
            (empty_memory ?r)
            (not (data_captured ?i))
        )
        :effect
        (and
            (data_captured ?d)
            (not (empty_memory ?r))
            (not (has_picture ?l ?i))
        )
    )
    
    (:action take_scan
        :parameters (?r - rover ?l - location ?sc - scan)
        :precondition
        (and
            (on_postion ?r ?l)
            (has_scan ?l ?sc)
            (empty_memory ?r)
            (not (data_captured ?sc))
        )
        :effect
        (and
            (data_captured ?sc)
            (not (empty_memory ?r))
            (not (has_scan ?l ?sc))
        )   
    )
    
    (:action take_sample
        :parameters (?r - rover ?l - location ?s - sample)
        :precondition
        (and
            (on_postion ?r ?l)
            (has_sample ?l ?s)
            (hand_empty ?r)
            (not (sample_collected ?s))
        )
        :effect
        (and
            (not (has_sample ?l ?s))
            (not (hand_empty ?r))
            (sample_collected ?s)
        )
    )
    
    (:action transmit_data
        :parameters (?r - rover ?d - data)
        :precondition (and 
            (captured_data ?r ?d)
            (not (has_received ?d))
        ) 
        :effect (and
            (not (captured_data ?r ?d))
            (has_received ?d)
            (memory_empty ?r)
            (not (captured_data ?r ?d))
        )
    )
    
    (:action sample_receive
        :parameters ()
        :precondition (and
            (not (is_full ?lan))
            (on_postion ?r ?l)
            (on_postion ?lan ?l)
            (collected_sample ?r ?s)
         )
        :effect (and 
            (is_full ?lan)
            (not (collected_sample ?r ?s))
            (hand_empty ?r)
            (has_received ?s)
        )
    )
    

        )